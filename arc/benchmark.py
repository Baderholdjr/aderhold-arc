"""Cross-client benchmark: aggregates only, never respondent-level data.

- Each campaign contributes its dimension and pillar indexes, but only if it was
  not suppressed (n >= min_group_size).
- Psychometrics use pooled responses from respondents who gave research consent
  (consent_research == 1). Only the resulting statistics are kept.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import psychometrics
from .instrument import Instrument
from .scoring import CampaignScore, clean


def _stats(values: list[float]) -> dict:
    a = np.array(values, dtype=float)
    return {"campaigns": int(len(a)), "mean": float(a.mean()), "p25": float(np.percentile(a, 25)),
            "median": float(np.median(a)), "p75": float(np.percentile(a, 75))}


def build(scores: list[CampaignScore], responses: pd.DataFrame, inst: Instrument,
          exclude_prefixes: tuple[str, ...] = ("DEMO", "TEST")) -> dict:
    # Benchmark = staff baselines only, so every client is compared at the same point and with the same wording.
    usable = [s for s in scores if not s.suppressed and not s.campaign.startswith(exclude_prefixes)
              and s.audience == "staff" and s.wave == "T1"]
    dims = {}
    for d in inst.dimensions:
        vals = [x.index_all for s in usable for x in s.dimensions if x.code == d.code and x.index_all is not None]
        dims[d.code] = _stats(vals) if vals else None
    pillars = {}
    for p in inst.pillars:
        vals = [x.index_all for s in usable for x in s.pillars if x.pillar == p and x.index_all is not None]
        pillars[p] = _stats(vals) if vals else None

    pooled = clean(responses, inst)
    pooled = pooled[(pooled["consent_research"] == 1) & ~pooled["campaign"].str.startswith(exclude_prefixes)
                    & (pooled["audience"] == "staff")]
    return {
        "instrument_version": inst.version,
        "campaigns_included": len(usable),
        "respondents_pooled_with_consent": int(len(pooled)),
        "dimensions": dims,
        "pillars": pillars,
        "reliability": psychometrics.reliability(pooled, inst) if len(pooled) >= psychometrics.MIN_N_ALPHA else
        f"Deferred until {psychometrics.MIN_N_ALPHA} consented responses",
        "structure": psychometrics.structure_check(pooled, inst) if len(pooled) >= len(inst.item_ids) else
        f"Deferred until {len(inst.item_ids)} complete consented responses",
    }


def percentile_rank(value: float | None, code: str, bench: dict | None) -> str | None:
    """Rough position against the benchmark quartiles, for client reports."""
    if value is None or not bench:
        return None
    b = (bench.get("dimensions") or {}).get(code)
    if not b or b["campaigns"] < 5:
        return None
    if value < b["p25"]:
        return "Bottom quartile"
    if value < b["median"]:
        return "Below median"
    if value < b["p75"]:
        return "Above median"
    return "Top quartile"
