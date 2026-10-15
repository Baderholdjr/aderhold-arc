"""Score A.R.C. Pulse Survey responses for one campaign or any pooled group of responses.

Rules (identical to the companion Excel workbook for the staff survey):
- Reverse-coded items are flipped: 6 - answer.
- Item mean is taken per group; dimension index = (mean of its item means - 1) / 4 * 100.
- Pillar index = mean of its dimension indexes; overall = mean of pillar indexes.
- Staff groups under 5 respondents are suppressed; the leadership survey reports at 3+.
- Within the staff survey, perception gap = Leaders (MGR+SL) index - IC index; flagged at >= 15.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field

import numpy as np
import pandas as pd

from .instrument import Instrument

STAFF_ROLES = ["IC", "MGR", "SL"]
ALL_ROLES = STAFF_ROLES + ["LEAD"]


def clean(df: pd.DataFrame, inst: Instrument) -> pd.DataFrame:
    """Coerce types, fill defaults for older rows, drop empty or duplicate submissions."""
    df = df.copy()
    for col in inst.columns:
        if col not in df.columns:
            df[col] = np.nan
    for col in inst.item_ids + [x["id"] for x in inst.leadership_items if x["type"] == "likert"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df.loc[~df[col].isin([1, 2, 3, 4, 5]), col] = np.nan
    for x in inst.exposure_items:
        df[x["id"]] = pd.to_numeric(df[x["id"]], errors="coerce")
        df.loc[~df[x["id"]].isin([0, 1]), x["id"]] = np.nan
    for x in inst.change_items:
        df[x["id"]] = pd.to_numeric(df[x["id"]], errors="coerce")
        df.loc[~df[x["id"]].isin([-2, -1, 0, 1, 2]), x["id"]] = np.nan
    for x in inst.leadership_items:
        if x["type"] == "choice":
            df[x["id"]] = pd.to_numeric(df[x["id"]], errors="coerce")
    for col in inst.behavioral_keys + ["consent_research"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["campaign"] = df["campaign"].astype(str).str.strip().str.upper()
    # Rows from instrument v1.0 have no engagement/wave/audience: treat them as a T1 staff campaign.
    eng = df["engagement"].where(df["engagement"].notna() & (df["engagement"].astype(str).str.strip() != ""))
    df["engagement"] = eng.fillna(df["campaign"]).astype(str).str.strip().str.upper()
    wave = df["wave"].astype(str).str.strip().str.upper()
    df["wave"] = wave.where(wave.isin(["T1", "T2", "T3"]), "T1")
    aud = df["audience"].astype(str).str.strip().str.lower()
    df["audience"] = aud.where(aud.isin(["staff", "leader"]), "staff")
    df["role"] = df["role"].astype(str).str.strip().str.upper()
    df.loc[df["audience"] == "leader", "role"] = "LEAD"
    df.loc[~df["role"].isin(ALL_ROLES), "role"] = np.nan

    answered = df[inst.item_ids].notna().sum(axis=1)
    df = df[answered >= len(inst.item_ids) / 2]  # a response must answer at least half the core items
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
        out[it.id] = None if pd.isna(m) else float(6 - m if it.reverse else m)
    return out


def respondent_indexes(df: pd.DataFrame, inst: Instrument) -> pd.DataFrame:
    """One row per respondent, one column per dimension (0-100), for statistical tests."""
    out = pd.DataFrame(index=df.index)
    for d in inst.dimensions:
        cols = []
        for it in d.items:
            v = pd.to_numeric(df[it.id], errors="coerce")
            cols.append(6 - v if it.reverse else v)
        out[d.code] = (pd.concat(cols, axis=1).mean(axis=1) - 1) / 4 * 100
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
    engagement: str = ""
    wave: str = "T1"
    audience: str = "staff"
    min_group_size: int = 5
    exposure: dict = field(default_factory=dict)
    change: dict = field(default_factory=dict)
    leadership: dict = field(default_factory=dict)

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


def exposure_summary(df: pd.DataFrame, inst: Instrument) -> dict:
    """Share answering Yes, among those answering Yes or No, for each module asked."""
    out = {}
    for x in inst.exposure_items:
        s = df[x["id"]].dropna()
        if len(s):
            out[x["module"]] = {"item": x["id"], "answered": int(len(s)), "reach": float(s.mean()),
                                "targets": x["targets"]}
    return out


def change_summary(df: pd.DataFrame, inst: Instrument) -> dict:
    out = {}
    for x in inst.change_items:
        s = df[x["id"]].dropna()
        if len(s):
            out[x["id"]] = {"text": x["text"], "pillar": x["pillar"], "answered": int(len(s)),
                            "mean": float(s.mean()), "share_better": float((s > 0).mean()),
                            "share_worse": float((s < 0).mean())}
    return out


def leadership_summary(df: pd.DataFrame, inst: Instrument) -> dict:
    out = {}
    for x in inst.leadership_items:
        s = df[x["id"]].dropna()
        if not len(s):
            continue
        if x["type"] == "likert":
            out[x["id"]] = {"text": x["text"], "answered": int(len(s)), "mean": float(s.mean()),
                            "share_agree": float((s >= 4).mean())}
        else:
            labels = {o["value"]: o["label"] for o in x["options"] if o["value"] is not None}
            counts = {labels.get(int(v), str(v)): int(c) for v, c in s.value_counts().sort_index().items()}
            out[x["id"]] = {"text": x["text"], "answered": int(len(s)), "counts": counts}
    return out


def score_frame(df: pd.DataFrame, inst: Instrument, label: str, audience: str | None = None,
                engagement: str = "", wave: str = "T1") -> CampaignScore:
    """Score an already-cleaned set of responses (a campaign, or a pooled engagement/wave/audience group)."""
    sc = inst.scoring
    groups = sc["groups"]
    if audience is None:
        audience = df["audience"].mode().iat[0] if len(df) else "staff"
    min_n = inst.min_group(audience)
    n = len(df)
    is_staff = audience == "staff"
    n_ic = int(df["role"].isin(groups["IC"]).sum()) if is_staff else 0
    n_lead = int(df["role"].isin(groups["Leaders"]).sum()) if is_staff else 0
    suppressed = n < min_n

    means_all = item_means(df, inst, None) if not suppressed else {}
    means_ic = item_means(df, inst, groups["IC"]) if is_staff and n_ic >= min_n else {}
    means_ld = item_means(df, inst, groups["Leaders"]) if is_staff and n_lead >= min_n else {}

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
        pillars.append(PillarScore(p, pa, _avg([d.index_ic for d in pd_]), _avg([d.index_leaders for d in pd_]),
                                   level, name))

    overall = _avg([p.index_all for p in pillars])
    ranked = sorted([d for d in dims if d.index_all is not None], key=lambda d: d.index_all)
    top = [{"rank": k + 1, "code": d.code, "name": d.name, "index": d.index_all, "severity": d.severity}
           for k, d in enumerate(ranked[:5])]

    return CampaignScore(
        campaign=label, instrument_version=inst.version, n=n, n_ic=n_ic, n_leaders=n_lead,
        suppressed=suppressed, dimensions=dims, pillars=pillars, overall_index=overall,
        top_gaps=top, behavioral=behavioral_signals(df) if not suppressed else {},
        engagement=engagement, wave=wave, audience=audience, min_group_size=min_n,
        exposure=exposure_summary(df, inst) if not suppressed else {},
        change=change_summary(df, inst) if not suppressed else {},
        leadership=leadership_summary(df, inst) if not suppressed else {},
    )


def score_campaign(df: pd.DataFrame, inst: Instrument, campaign: str | None = None) -> CampaignScore:
    df = clean(df, inst)
    if campaign:
        df = df[df["campaign"] == campaign.upper()]
    label = campaign or (df["campaign"].iloc[0] if len(df) else "UNKNOWN")
    meta = df.iloc[0] if len(df) else None
    return score_frame(df, inst, label,
                       audience=None if meta is None else meta["audience"],
                       engagement="" if meta is None else meta["engagement"],
                       wave="T1" if meta is None else meta["wave"])


def _avg(values):
    vals = [v for v in values if v is not None]
    return float(np.mean(vals)) if vals else None
