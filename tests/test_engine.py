"""Engine tests. The demo data is the same synthetic set as the Excel workbook, so these
values are cross-checked against the workbook's own formulas (LibreOffice-recalculated)."""
import numpy as np
import pandas as pd
import pytest

from arc import psychometrics, roi
from arc.instrument import load
from arc.scoring import clean, item_means, score_campaign

INST = load()
DEMO = pd.read_csv("data/demo/demo_responses.csv", dtype=str)


def dim(score, code):
    return next(d for d in score.dimensions if d.code == code)


def test_instrument_shape():
    assert len(INST.items) == 45
    assert len(INST.dimensions) == 15
    assert sum(i.reverse for i in INST.items) == 9


def test_matches_workbook_dimension_indexes():
    s = score_campaign(DEMO, INST, "DEMO-2026Q4")
    assert s.n == 40 and s.n_ic == 28 and s.n_leaders == 12
    assert dim(s, "A1").index_all == pytest.approx(69.5833, abs=1e-3)
    assert dim(s, "A1").index_ic == pytest.approx(61.6071, abs=1e-3)
    assert dim(s, "A1").index_leaders == pytest.approx(88.1944, abs=1e-3)
    assert dim(s, "R4").index_all == pytest.approx(26.875, abs=1e-3)
    assert dim(s, "F1").perception_gap == pytest.approx(35.5159, abs=1e-3)
    assert dim(s, "A3").severity == "Critical"
    assert dim(s, "A1").flag == "Perception gap"


def test_matches_workbook_pillars_and_top_gaps():
    s = score_campaign(DEMO, INST, "DEMO-2026Q4")
    p = {x.pillar: x for x in s.pillars}
    assert p["Acceptance"].index_all == pytest.approx(54.84375, abs=1e-4)
    assert p["Reliance"].level == 2 and p["Reliance"].level_name == "Tolerated"
    assert s.overall_index == pytest.approx(44.0885, abs=1e-3)
    assert [g["code"] for g in s.top_gaps] == ["R4", "R3", "A3", "R1", "C4"]


def test_behavioral_signals():
    b = score_campaign(DEMO, INST, "DEMO-2026Q4").behavioral
    assert b["active_adoption"] == pytest.approx(0.75)
    assert b["verification_share"] == pytest.approx(0.41875)
    assert b["shadow_ai_30d"] == pytest.approx(0.475)


def test_reverse_coding():
    row = {c: None for c in INST.columns}
    rows = []
    for k in range(5):
        r = dict(row, response_id=f"x{k}", campaign="T", role="IC", consent_research=1)
        for i in INST.item_ids:
            r[i] = 5
        rows.append(r)
    m = item_means(clean(pd.DataFrame(rows), INST), INST, None)
    assert m["A1.1"] == 5 and m["A2.2"] == 1  # A2.2 is reverse-coded


def test_small_groups_are_suppressed():
    small = DEMO.head(4)
    s = score_campaign(small, INST, "DEMO-2026Q4")
    assert s.suppressed and s.overall_index is None and s.behavioral == {}
    only_ic = DEMO[DEMO["role"] == "IC"]
    s2 = score_campaign(only_ic, INST, "DEMO-2026Q4")
    assert all(d.index_leaders is None for d in s2.dimensions)


def test_invalid_answers_and_duplicates_are_cleaned():
    bad = DEMO.copy()
    bad.loc[0, "A1.1"] = "9"
    dup = pd.concat([bad, bad.head(3)])
    c = clean(dup, INST)
    assert len(c) == 40
    assert np.isnan(c.loc[0, "A1.1"])


def test_roi_matches_playbook_example():
    cfg = {"overrides": {"adoption": 0.45, "depth": 0.40, "verification": 0.40, "capture": 0.50},
           "errors_per_year": 12, "cost_per_error": 25000}
    r = roi.compute({}, None, cfg)
    assert r.achievable_value == pytest.approx(3_312_000)
    assert r.current_value == pytest.approx(223_560)
    assert r.target_value == pytest.approx(1_135_265.625)
    assert r.recoverable_value == pytest.approx(1_157_330.625)
    assert r.net_return_x == pytest.approx(6.7155, abs=1e-3)
    assert r.waterfall[-1]["running"] == pytest.approx(r.current_value)


def test_roi_requires_factors():
    with pytest.raises(ValueError):
        roi.compute({}, None, {})


def test_cronbach_alpha_known_value():
    x = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [2, 3, 3, 4, 5], "c": [1, 2, 4, 4, 5]})
    # Hand-computed: item variances 2.5, 1.3, 2.7 (sum 6.5); total-score variance 18.3
    assert psychometrics.cronbach_alpha(x) == pytest.approx(1.5 * (1 - 6.5 / 18.3))


def test_reliability_runs_on_demo():
    rel = psychometrics.reliability(clean(DEMO, INST), INST)
    assert len(rel) == 15 and all(r["n"] > 0 for r in rel)
