"""Three-wave and leadership analytics (instrument v1.1)."""
import pandas as pd
import pytest
import yaml

from arc import sources, waves
from arc.instrument import load
from arc.scoring import clean, score_frame

INST = load()
ALL = clean(sources.from_csv("data/demo", INST), INST)
CFG = yaml.safe_load(open("engagements/DEMO.yaml"))["roi"]
EA = waves.analyze(ALL, INST, "DEMO", CFG)


def _rows(n, audience, value=4):
    rows = []
    for k in range(n):
        r = {c: None for c in INST.columns}
        r.update(response_id=f"{audience}{k}", campaign="T", engagement="E", wave="T1", audience=audience,
                 role="IC", consent_research=1)
        for i in INST.item_ids:
            r[i] = value
        rows.append(r)
    return clean(pd.DataFrame(rows), INST)


def test_instrument_v11_modules():
    assert INST.version == "1.1.0"
    assert all(i.leader_text for i in INST.items)
    assert len(INST.exposure_items) == 12 and len(INST.change_items) == 5 and len(INST.leadership_items) == 7
    assert INST.min_group("leader") == 3 and INST.min_group("staff") == 5


def test_legacy_rows_default_to_t1_staff():
    legacy = pd.DataFrame([{"response_id": "x", "campaign": "old-1", "role": "IC", **{i: 3 for i in INST.item_ids}}])
    c = clean(legacy, INST)
    assert c.loc[0, "engagement"] == "OLD-1" and c.loc[0, "wave"] == "T1" and c.loc[0, "audience"] == "staff"


def test_leadership_reports_at_three():
    assert not score_frame(_rows(3, "leader"), INST, "L", "leader").suppressed
    assert score_frame(_rows(2, "leader"), INST, "L", "leader").suppressed
    assert score_frame(_rows(4, "staff"), INST, "S", "staff").suppressed
    lead = clean(pd.DataFrame([{**{c: None for c in INST.columns}, "response_id": "a", "campaign": "L",
                                "audience": "leader", "role": "IC", **{i: 3 for i in INST.item_ids}}]), INST)
    assert lead.loc[0, "role"] == "LEAD"


def test_change_rule_needs_points_and_significance():
    rules = INST.change_rules
    assert waves.classify(8.0, 0.01, rules) == "Improved"
    assert waves.classify(-6.0, 0.03, rules) == "Declined"
    assert waves.classify(4.9, 0.0001, rules) == "No reliable change"   # significant but too small
    assert waves.classify(12.0, 0.2, rules) == "No reliable change"     # large but not significant
    assert waves.classify(None, None, rules) == "Not comparable"


def test_demo_engagement_story():
    assert set(EA.groups) == {"T1/staff", "T1/leader", "T2/staff", "T3/staff", "T3/leader"}
    t13 = next(c for c in EA.comparisons if c.audience == "staff" and (c.from_wave, c.to_wave) == ("T1", "T3"))
    assert t13.summary["Improved"] == 10 and t13.summary["Declined"] == 0
    a3 = next(r for r in t13.rows if r["code"] == "A3")
    assert a3["delta"] > 20 and a3["p"] < 0.001
    m7_t2 = next(x for x in EA.exposure["T2"] if x["module"] == "M7")
    assert m7_t2["status"] == "Not reaching people" and m7_t2["reach"] < 0.5
    assert all(x["status"] == "Working" for x in EA.exposure["T3"])
    assert sum(1 for g in EA.leader_gaps["T1"] if g["flag"]) == 6
    assert EA.value["T3"]["recovered_vs_T1"] > 0 and EA.value["T1"]["recovered_vs_T1"] == 0


def test_exposure_values_are_validated():
    df = _rows(5, "staff")
    raw = df.copy()
    raw["X.M3"] = [1, 0, 7, "yes", None]
    c = clean(raw, INST)
    assert c["X.M3"].tolist()[:2] == [1, 0] and c["X.M3"].isna().sum() == 3


def test_leader_campaign_has_leadership_module():
    s = EA.groups["T3/leader"]
    assert s.audience == "leader" and s.n == 5 and "L1" in s.leadership and "counts" in s.leadership["L7"]


def test_earlier_version_tabs_are_read():
    f = sources.is_responses_tab
    assert f("Responses") and f("Responses v1.0.0") and f("Responses (earlier version)")
    assert not f("Campaigns") and not f("Responses notes")
