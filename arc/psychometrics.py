"""Reliability and structure statistics for validating the A.R.C. instrument.

Run on pooled, consented responses across campaigns (see benchmark.py).

- Cronbach's alpha per dimension (target >= 0.70), alpha-if-item-deleted and
  corrected item-total correlations (flag items < 0.30).
- Horn's parallel analysis: how many factors the data support.
- Exploratory factor analysis (principal-axis factoring + varimax) once the
  pooled sample reaches MIN_N_EFA, with a "structure match" rate: the share of
  items whose strongest loading is on the factor where most of their own
  dimension's items load.
Only numpy is required, so this runs in GitHub Actions without heavy packages.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .instrument import Instrument

MIN_N_ALPHA = 30
MIN_N_EFA = 200


def adjusted_items(df: pd.DataFrame, inst: Instrument) -> pd.DataFrame:
    """Item matrix with reverse-coded items flipped (6 - x)."""
    out = pd.DataFrame(index=df.index)
    for it in inst.items:
        col = pd.to_numeric(df[it.id], errors="coerce")
        out[it.id] = 6 - col if it.reverse else col
    return out


def cronbach_alpha(x: pd.DataFrame) -> float | None:
    x = x.dropna()
    k = x.shape[1]
    if k < 2 or len(x) < 3:
        return None
    item_var = x.var(axis=0, ddof=1).sum()
    total_var = x.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return None
    return float(k / (k - 1) * (1 - item_var / total_var))


def reliability(df: pd.DataFrame, inst: Instrument) -> list[dict]:
    adj = adjusted_items(df, inst)
    rows = []
    for d in inst.dimensions:
        ids = [i.id for i in d.items]
        x = adj[ids].dropna()
        alpha = cronbach_alpha(x)
        items = []
        for i in ids:
            rest = x.drop(columns=i).sum(axis=1)
            r = float(np.corrcoef(x[i], rest)[0, 1]) if len(x) > 2 and x[i].std() > 0 and rest.std() > 0 else None
            items.append({"item": i, "corrected_item_total": r,
                          "alpha_if_deleted": cronbach_alpha(x.drop(columns=i)),
                          "flag": (r is not None and r < 0.30)})
        rows.append({"dimension": d.code, "n": int(len(x)), "alpha": alpha,
                     "meets_0_70": (alpha is not None and alpha >= 0.70), "items": items})
    return rows


def _corr(adj: pd.DataFrame) -> np.ndarray:
    return adj.dropna().corr().to_numpy()


def parallel_analysis(adj: pd.DataFrame, iterations: int = 100, seed: int = 0) -> dict:
    x = adj.dropna().to_numpy()
    n, k = x.shape
    if n < k:
        return {"n": n, "suggested_factors": None, "note": "Not enough complete responses"}
    obs = np.sort(np.linalg.eigvalsh(np.corrcoef(x, rowvar=False)))[::-1]
    rng = np.random.default_rng(seed)
    sims = np.empty((iterations, k))
    for b in range(iterations):
        sims[b] = np.sort(np.linalg.eigvalsh(np.corrcoef(rng.standard_normal((n, k)), rowvar=False)))[::-1]
    thresh = np.percentile(sims, 95, axis=0)
    count = 0
    for o, t in zip(obs, thresh):
        if o > t:
            count += 1
        else:
            break
    return {"n": n, "suggested_factors": count, "observed_eigenvalues": obs[:20].round(3).tolist()}


def _varimax(L: np.ndarray, iters: int = 100, tol: float = 1e-6) -> np.ndarray:
    p, k = L.shape
    R = np.eye(k)
    d = 0.0
    for _ in range(iters):
        Lr = L @ R
        u, s, vt = np.linalg.svd(L.T @ (Lr ** 3 - Lr @ np.diag((Lr ** 2).sum(axis=0)) / p))
        R = u @ vt
        d_new = s.sum()
        if d_new < d * (1 + tol):
            break
        d = d_new
    return L @ R


def principal_axis(adj: pd.DataFrame, n_factors: int, iters: int = 200) -> np.ndarray:
    R = _corr(adj)
    h2 = 1 - 1 / np.diag(np.linalg.pinv(R))  # squared multiple correlations
    for _ in range(iters):
        Rr = R.copy()
        np.fill_diagonal(Rr, h2)
        vals, vecs = np.linalg.eigh(Rr)
        idx = np.argsort(vals)[::-1][:n_factors]
        L = vecs[:, idx] * np.sqrt(np.clip(vals[idx], 0, None))
        new_h2 = np.clip((L ** 2).sum(axis=1), 0, 1)
        if np.max(np.abs(new_h2 - h2)) < 1e-5:
            break
        h2 = new_h2
    return _varimax(L)


def structure_check(df: pd.DataFrame, inst: Instrument) -> dict:
    adj = adjusted_items(df, inst)
    n = int(len(adj.dropna()))
    pa = parallel_analysis(adj)
    if n < MIN_N_EFA:
        return {"n_complete": n, "status": f"EFA deferred until {MIN_N_EFA} complete responses",
                "parallel_analysis": pa}
    k = len(inst.dimensions)
    L = principal_axis(adj, k)
    primary = np.abs(L).argmax(axis=1)
    ids = inst.item_ids
    matches = 0
    for d in inst.dimensions:
        pos = [ids.index(i.id) for i in d.items]
        home = np.bincount(primary[pos], minlength=k).argmax()
        matches += int(sum(primary[p_] == home for p_ in pos))
    return {"n_complete": n, "status": "EFA complete", "n_factors": k,
            "structure_match_rate": matches / len(ids), "parallel_analysis": pa,
            "loadings": {i: L[j].round(3).tolist() for j, i in enumerate(ids)}}
