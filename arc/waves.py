"""Engagement analysis across the three waves and the two audiences.

An engagement (one client program) has up to three waves (T1 baseline, T2 midpoint, T3 follow-up)
and two audiences (staff, leader). Responses are compared at group level only: no individual is
followed between waves, so anonymity is preserved.

- Change between waves, per dimension: the difference in index, a Welch t-test on respondent-level
  dimension scores and Cohen's d. "Improved" or "Declined" requires BOTH a move of at least
  `min_points` index points AND p < `alpha`; anything else is "No reliable change".
- Leader-vs-staff gap, per dimension and wave: leader index minus staff index (flag at 15+ points).
- Exposure check (T2/T3): did each implemented recommendation reach people, and is it associated
  with the dimensions it targets (exposed vs. not exposed within the wave)?
- Value recovered: realized annual value at each wave from that wave's survey factors, minus T1.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field

import numpy as np
import pandas as pd
from scipy import stats

from . import roi as roi_mod
from .instrument import Instrument
from .scoring import CampaignScore, item_means, respondent_indexes, score_frame

WAVE_ORDER = ["T1", "T2", "T3"]
WAVE_NAMES = {"T1": "Baseline", "T2": "Midpoint", "T3": "Follow-up"}


@dataclass
class Comparison:
    audience: str
    from_wave: str
    to_wave: str
    rows: list[dict]           # per dimension: code, name, pillar, from, to, delta, p, d, status
    pillars: list[dict]        # per pillar: from, to, delta
    summary: dict              # counts of improved / declined / no reliable change


@dataclass
class EngagementAnalysis:
    engagement: str
    groups: dict = field(default_factory=dict)        # "T1/staff" -> CampaignScore
    comparisons: list[Comparison] = field(default_factory=list)
    leader_gaps: dict = field(default_factory=dict)   # wave -> list of per-dimension gaps
    exposure: dict = field(default_factory=dict)      # wave -> list of module diagnostics
    value: dict = field(default_factory=dict)         # wave -> realized value, recovered vs T1

    def to_dict(self) -> dict:
        d = asdict(self)
        d["groups"] = {k: v.to_dict() for k, v in self.groups.items()}
        return d


def _welch(a: pd.Series, b: pd.Series) -> tuple[float | None, float | None]:
    a, b = a.dropna(), b.dropna()
    if len(a) < 2 or len(b) < 2 or (a.std() == 0 and b.std() == 0):
        return None, None
    t = stats.ttest_ind(b, a, equal_var=False)
    sd = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    d = float((b.mean() - a.mean()) / sd) if sd > 0 else None
    return float(t.pvalue), d


def classify(delta: float | None, p: float | None, rules: dict) -> str:
    if delta is None:
        return "Not comparable"
    if p is not None and p < rules["alpha"] and abs(delta) >= rules["min_points"]:
        return "Improved" if delta > 0 else "Declined"
    return "No reliable change"


def compare(df_a: pd.DataFrame, df_b: pd.DataFrame, sa: CampaignScore, sb: CampaignScore,
            inst: Instrument, audience: str, wa: str, wb: str) -> Comparison:
    rules = inst.change_rules
    ra, rb = respondent_indexes(df_a, inst), respondent_indexes(df_b, inst)
    rows = []
    for da, db in zip(sa.dimensions, sb.dimensions):
        delta = (db.index_all - da.index_all) if (da.index_all is not None and db.index_all is not None) else None
        p, d = _welch(ra[da.code], rb[da.code]) if delta is not None else (None, None)
        rows.append({"code": da.code, "name": da.name, "pillar": da.pillar, "from": da.index_all,
                     "to": db.index_all, "delta": delta, "p": p, "d": d, "status": classify(delta, p, rules)})
    pillars = []
    for pa, pb in zip(sa.pillars, sb.pillars):
        delta = (pb.index_all - pa.index_all) if (pa.index_all is not None and pb.index_all is not None) else None
        pillars.append({"pillar": pa.pillar, "from": pa.index_all, "to": pb.index_all, "delta": delta,
                        "from_level": pa.level, "to_level": pb.level})
    summary = {s: sum(r["status"] == s for r in rows)
               for s in ("Improved", "Declined", "No reliable change", "Not comparable")}
    return Comparison(audience, wa, wb, rows, pillars, summary)


def leader_staff_gaps(staff: CampaignScore, leader: CampaignScore, inst: Instrument) -> list[dict]:
    out = []
    flag_at = inst.change_rules["leader_staff_gap_points"]
    for ds, dl in zip(staff.dimensions, leader.dimensions):
        gap = (dl.index_all - ds.index_all) if (ds.index_all is not None and dl.index_all is not None) else None
        out.append({"code": ds.code, "name": ds.name, "pillar": ds.pillar, "staff": ds.index_all,
                    "leader": dl.index_all, "gap": gap,
                    "flag": ("Leaders see it better" if gap is not None and gap >= flag_at else
                             "Leaders see it worse" if gap is not None and gap <= -flag_at else None)})
    return out


def exposure_diagnostics(df_wave: pd.DataFrame, score_wave: CampaignScore, comp_from_t1: Comparison | None,
                         inst: Instrument) -> list[dict]:
    rules = inst.change_rules
    min_n = inst.min_group("staff")
    rix = respondent_indexes(df_wave, inst)
    status_by_dim = {r["code"]: r for r in (comp_from_t1.rows if comp_from_t1 else [])}
    out = []
    for module, e in score_wave.exposure.items():
        targets = e["targets"]
        col = df_wave[e["item"]]
        target_score = rix[targets].mean(axis=1)
        yes, no = target_score[col == 1], target_score[col == 0]
        exposed_diff = None
        if len(yes.dropna()) >= min_n and len(no.dropna()) >= min_n:
            exposed_diff = float(yes.mean() - no.mean())
        moves = [status_by_dim[t]["status"] for t in targets if t in status_by_dim]
        if e["reach"] < rules["exposure_reach_threshold"]:
            status = "Not reaching people"
        elif "Improved" in moves:
            status = "Working"
        elif "Declined" in moves:
            status = "Reaching people, moving the wrong way"
        elif moves:
            status = "Reaching people, not yet moving"
        else:
            status = "Reaching people (no baseline to compare)"
        out.append({"module": module, "reach": e["reach"], "answered": e["answered"], "targets": targets,
                    "target_changes": {t: status_by_dim[t]["delta"] for t in targets if t in status_by_dim},
                    "exposed_minus_unexposed": exposed_diff, "status": status})
    return sorted(out, key=lambda r: int(r["module"][1:]))


def wave_value(df_wave: pd.DataFrame, score_wave: CampaignScore, inst: Instrument, cfg: dict | None) -> dict | None:
    """Realized annual value from this wave's survey factors (overrides ignored, for comparability)."""
    if not cfg or score_wave.suppressed:
        return None
    c13 = item_means(df_wave, inst, None).get("C1.3")
    clean_cfg = {k: v for k, v in cfg.items() if k != "overrides"}
    try:
        r = roi_mod.compute(score_wave.behavioral, (c13 / 5) if c13 else None, clean_cfg)
    except ValueError:
        return None
    return {"achievable": r.achievable_value, "realized": r.current_value, "share_realized": r.share_realized,
            "factors": r.factors_current}


def analyze(cleaned: pd.DataFrame, inst: Instrument, engagement: str, roi_cfg: dict | None = None) -> EngagementAnalysis:
    sub = cleaned[cleaned["engagement"] == engagement]
    ea = EngagementAnalysis(engagement)
    frames = {}
    for wave in WAVE_ORDER:
        for aud in ("staff", "leader"):
            part = sub[(sub["wave"] == wave) & (sub["audience"] == aud)]
            if len(part):
                key = f"{wave}/{aud}"
                frames[key] = part
                ea.groups[key] = score_frame(part, inst, f"{engagement} {wave} {aud}", aud, engagement, wave)

    for aud in ("staff", "leader"):
        present = [w for w in WAVE_ORDER if f"{w}/{aud}" in ea.groups and not ea.groups[f"{w}/{aud}"].suppressed]
        pairs = [(present[i], present[j]) for i in range(len(present)) for j in range(i + 1, len(present))]
        for wa, wb in pairs:
            ka, kb = f"{wa}/{aud}", f"{wb}/{aud}"
            ea.comparisons.append(compare(frames[ka], frames[kb], ea.groups[ka], ea.groups[kb], inst, aud, wa, wb))

    for wave in WAVE_ORDER:
        s, l = ea.groups.get(f"{wave}/staff"), ea.groups.get(f"{wave}/leader")
        if s and l and not s.suppressed and not l.suppressed:
            ea.leader_gaps[wave] = leader_staff_gaps(s, l, inst)

    for wave in ("T2", "T3"):
        key = f"{wave}/staff"
        if key in ea.groups and not ea.groups[key].suppressed and ea.groups[key].exposure:
            comp = next((c for c in ea.comparisons if c.audience == "staff" and c.from_wave == "T1"
                         and c.to_wave == wave), None)
            ea.exposure[wave] = exposure_diagnostics(frames[key], ea.groups[key], comp, inst)

    base = None
    for wave in WAVE_ORDER:
        key = f"{wave}/staff"
        if key in ea.groups:
            v = wave_value(frames[key], ea.groups[key], inst, roi_cfg)
            if v:
                if base is None and wave == "T1":
                    base = v["realized"]
                v["recovered_vs_T1"] = (v["realized"] - base) if base is not None else None
                ea.value[wave] = v
    return ea
