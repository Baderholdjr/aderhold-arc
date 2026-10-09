"""Score A.R.C. Pulse Survey responses for one campaign (one client survey wave).

Rules (identical to the companion Excel workbook):
- Reverse-coded items are flipped: 6 - answer.
- Item mean is taken per group; dimension index = (mean of its item means - 1) / 4 * 100.
- Pillar index = mean of its dimension indexes; overall = mean of pillar indexes.
- Any group with fewer than `min_group_size` respondents is suppressed (None).
- Perception gap = Leaders index - IC index; flagged at >= perception_gap_points.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd

from .instrument import Instrument


def clean(df: pd.DataFrame, inst: Instrument) -> pd.DataFrame:
    """Coerce types, drop empty or duplicate submissions. Never mutates the input."""
    df = df.copy()
    for col in inst.columns:
        if col not in df.columns:
            df[col] = np.nan
    for col in inst.item_ids:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df.loc[~df[col].isin([1, 2, 3, 4, 5]), col] = np.nan
    for col in inst.behavioral_keys + ["consent_research"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["role"] = df["role"].astype(str).str.strip().str.upper()
    df.loc[~df["role"].isin(["IC", "MGR", "SL"]), "role"] = np.nan
    df["campaign"] = df["campaign"].astype(str).str.strip().str.upper()
    answered = df[inst.item_ids].notna().sum(axis=1)
    # A response must answer at least half the items to count.
    df = df[answered >= len(inst.item_ids) / 2]
    if "response_id" in df.columns:
        df = df.drop_duplicates(subset="response_id", keep="first")
    return df.reset_index(drop=True)


def _group_mask(df: pd.DataFrame, roles: list[str] | None) -> pd.Series:
    if roles is None:
        return pd.Series(True, index=df.index)
    return df["role"].isin(roles)


def item_means(df: pd.DataFrame, inst: Instrument, roles: list[str] | None) -> dict[str, float]:
    sub = df[_group_mask(df, roles)]
    out = {}
    for it in inst.items:
        m = sub[it.id].mean()
        if pd.isna(m):
            out[it.id] = None
        else:
            out[it.id] = float(6 - m if it.reverse else m)
    return out


def _index(values: list[float | None]) -> float | None:
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return (float(np.mean(vals)) - 1) / 4 * 100


@dataclass
class DimensionScore:
    code: str
    name: str
    pillar: str
    index_all: float | None
    index_ic: float | None
    index_leaders: float | None
    perception_gap: float | None
    severity: str | None
    flag: str | None


@dataclass
class PillarScore:
    pillar: str
    index_all: float | None
    index_ic: float | None
    index_leaders: float | None
    level: int | None
    level_name: str | None


@dataclass
class CampaignScore:
    campaign: str
    instrument_version: str
    n: int
    n_ic: int
    n_leaders: int
    suppressed: bool
    dimensions: list[DimensionScore]
    pillars: list[PillarScore]
    overall_index: float | None
    top_gaps: list[dict]
    behavioral: dict

    def to_dict(self) -> dict:
        return asdict(self)


def behavioral_signals(df: pd.DataFrame) -> dict:
    def share(col, cond):
        s = df[col].dropna()
        return float(cond(s).mean()) if len(s) else None

    def mean(col):
        s = df[col].dropna()
        return float(s.mean()) if len(s) else None

    return {
        "active_adoption": share("use_freq", lambda s: s >= 3),
        "depth_of_use": mean("depth"),
        "verification_share": mean("verify_share"),
        "error_seen_90d": mean("error_seen"),
        "training_hours_avg": mean("train_hrs"),
        "share_under_5_training_hours": share("train_hrs", lambda s: s < 5),
        "own_time_hours_avg": mean("own_time_hrs"),
        "shadow_ai_30d": mean("shadow_ai"),
    }


def score_campaign(df: pd.DataFrame, inst: Instrument, campaign: str | None = None) -> CampaignScore:
    sc = inst.scoring
    min_n = sc["min_group_size"]
    groups = sc["groups"]
    df = clean(df, inst)
    if campaign:
        df = df[df["campaign"] == campaign.upper()]
    campaign = campaign or (df["campaign"].iloc[0] if len(df) else "UNKNOWN")

    n = len(df)
    n_ic = int(df["role"].isin(groups["IC"]).sum())
    n_lead = int(df["role"].isin(groups["Leaders"]).sum())
    suppressed = n < min_n

    means_all = item_means(df, inst, None) if not suppressed else {}
    means_ic = item_means(df, inst, groups["IC"]) if n_ic >= min_n else {}
    means_ld = item_means(df, inst, groups["Leaders"]) if n_lead >= min_n else {}

    dims: list[DimensionScore] = []
    for d in inst.dimensions:
        ids = [i.id for i in d.items]
        ia = _index([means_all.get(i) for i in ids]) if means_all else None
        ic = _index([means_ic.get(i) for i in ids]) if means_ic else None
        il = _index([means_ld.get(i) for i in ids]) if means_ld else None
        gap = (il - ic) if (ic is not None and il is not None) else None
        flag = "Perception gap" if gap is not None and gap >= sc["perception_gap_points"] else None
        dims.append(DimensionScore(d.code, d.name, d.pillar, ia, ic, il, gap, inst.severity(ia), flag))

    pillars: list[PillarScore] = []
    for p in inst.pillars:
        pd_ = [d for d in dims if d.pillar == p]
        pa = _avg([d.index_all for d in pd_])
        level, name = inst.maturity(pa)
        pillars.append(PillarScore(p, pa, _avg([d.index_ic for d in pd_]), _avg([d.index_leaders for d in pd_]), level, name))

    overall = _avg([p.index_all for p in pillars])
    ranked = sorted([d for d in dims if d.index_all is not None], key=lambda d: d.index_all)
    top = [{"rank": k + 1, "code": d.code, "name": d.name, "index": d.index_all, "severity": d.severity}
           for k, d in enumerate(ranked[:5])]

    return CampaignScore(
        campaign=campaign, instrument_version=inst.version, n=n, n_ic=n_ic, n_leaders=n_lead,
        suppressed=suppressed, dimensions=dims, pillars=pillars, overall_index=overall,
        top_gaps=top, behavioral=behavioral_signals(df) if not suppressed else {},
    )


def _avg(values):
    vals = [v for v in values if v is not None]
    return float(np.mean(vals)) if vals else None
