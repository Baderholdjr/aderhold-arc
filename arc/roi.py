"""A.R.C. Value Leakage (ROI) model. Same formulas as the playbook and workbook.

    V0 (achievable) = N * H * (1 - v*) * W * T
    V  (realized)   = N * a * d * H * (1 - v) * c * W * T
    Recoverable     = (V_target - V_current) + avoided error cost + avoided attrition cost
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

DEFAULTS = {
    "users": 500,
    "hours_saved_per_week": 3.0,
    "loaded_hourly_cost": 60.0,
    "working_weeks": 46,
    "healthy_verification_share": 0.20,
    "tool_cost_per_user_year": 360.0,
    "overrides": {},  # adoption / depth / verification / capture: use instead of survey values
    "targets": {"adoption": 0.75, "depth": 0.65, "verification": 0.25, "capture": 0.75},
    "errors_per_year": 0,
    "cost_per_error": 0.0,
    "error_reduction": 0.5,
    "turnover_rate": 0.15,
    "ai_attributable_turnover_share": 0.10,
    "average_salary": 85000.0,
    "replacement_cost_pct": 0.5,
    "attrition_reduction": 0.30,
    "confidence_haircut": 0.5,
    "engagement_fee": 150000.0,
}


@dataclass
class RoiResult:
    factors_survey: dict
    factors_current: dict
    factors_target: dict
    achievable_value: float
    current_value: float
    target_value: float
    share_realized: float
    waterfall: list[dict]
    error_cost_current: float
    error_cost_target: float
    attrition_cost_current: float
    attrition_cost_target: float
    recoverable_value: float
    risk_adjusted_value: float
    engagement_fee: float
    net_return_x: float | None
    net_return_risk_adjusted_x: float | None
    payback_months: float | None

    def to_dict(self) -> dict:
        return asdict(self)


def _merge(cfg: dict | None) -> dict:
    out = {**DEFAULTS, **(cfg or {})}
    out["overrides"] = {**DEFAULTS["overrides"], **((cfg or {}).get("overrides") or {})}
    out["targets"] = {**DEFAULTS["targets"], **((cfg or {}).get("targets") or {})}
    return out


def value(N, a, d, H, v, c, W, T) -> float:
    return N * a * d * H * (1 - v) * c * W * T


def compute(behavioral: dict, capture_proxy: float | None, cfg: dict | None = None) -> RoiResult:
    p = _merge(cfg)
    N, H, W, T, vs = (p["users"], p["hours_saved_per_week"], p["loaded_hourly_cost"],
                      p["working_weeks"], p["healthy_verification_share"])
    survey = {
        "adoption": behavioral.get("active_adoption"),
        "depth": behavioral.get("depth_of_use"),
        "verification": behavioral.get("verification_share"),
        "capture": capture_proxy,
    }
    cur = {k: (p["overrides"][k] if p["overrides"].get(k) is not None else survey[k]) for k in survey}
    missing = [k for k, v in cur.items() if v is None]
    if missing:
        raise ValueError(f"No survey value or override for: {', '.join(missing)}")
    tgt = p["targets"]

    v0 = N * H * (1 - vs) * W * T
    vc = value(N, cur["adoption"], cur["depth"], H, cur["verification"], cur["capture"], W, T)
    vt = value(N, tgt["adoption"], tgt["depth"], H, tgt["verification"], tgt["capture"], W, T)

    steps = [("Low adoption", cur["adoption"]), ("Shallow use", cur["depth"]),
             ("Excess re-checking", (1 - cur["verification"]) / (1 - vs)), ("Time not redeployed", cur["capture"])]
    run, wf = v0, [{"step": "Achievable value", "lost": None, "running": v0}]
    for label, f in steps:
        lost = run * (1 - f)
        run -= lost
        wf.append({"step": label, "lost": lost, "running": run})
    wf.append({"step": "Realized value", "lost": None, "running": run})

    err_c = p["errors_per_year"] * p["cost_per_error"]
    err_t = err_c * (1 - p["error_reduction"])
    att_c = N * p["turnover_rate"] * p["ai_attributable_turnover_share"] * p["average_salary"] * p["replacement_cost_pct"]
    att_t = att_c * (1 - p["attrition_reduction"])
    rec = (vt - vc) + (err_c - err_t) + (att_c - att_t)
    risk = rec * (1 - p["confidence_haircut"])
    fee = p["engagement_fee"]

    return RoiResult(
        factors_survey=survey, factors_current=cur, factors_target=dict(tgt),
        achievable_value=v0, current_value=vc, target_value=vt,
        share_realized=(vc / v0) if v0 else 0.0, waterfall=wf,
        error_cost_current=err_c, error_cost_target=err_t,
        attrition_cost_current=att_c, attrition_cost_target=att_t,
        recoverable_value=rec, risk_adjusted_value=risk, engagement_fee=fee,
        net_return_x=((rec - fee) / fee) if fee else None,
        net_return_risk_adjusted_x=((risk - fee) / fee) if fee else None,
        payback_months=(fee / rec * 12) if rec > 0 else None,
    )
