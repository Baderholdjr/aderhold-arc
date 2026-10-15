"""Generate the synthetic DEMO engagement (all three waves, staff and leadership surveys).

The T1 staff file (data/demo/demo_responses.csv) is the same 40 responses as the Excel workbook
and is left untouched apart from its engagement/wave/audience columns. This script writes the
other waves. The story it tells (used in the manual and tests):
  - Implemented at T1: M3 role-based onboarding, M6 proportionate verification, M7 flop protocol,
    M11 governance for leaders.
  - T2: onboarding and verification are reaching people and moving A3, R3, F2; the flop protocol
    is NOT reaching people (reach ~35%), so R4 hasn't moved yet.
  - T3: the flop protocol was relaunched; most targets improved. C4 (expertise pipeline) declined,
    an unintended effect worth discussing.
  - Leaders rate A1, A3, F1 and F2 well above staff (classic perception gap).
Run:  python tools/make_demo.py
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

from arc.instrument import ROOT, load

INST = load()
OUT = ROOT / "data" / "demo"
BASE = {'A1': 3.6, 'A2': 2.9, 'A3': 2.2, 'A4': 3.8, 'R1': 2.6, 'R2': 2.7, 'R3': 2.3, 'R4': 2.0,
        'C1': 2.4, 'C2': 3.1, 'C3': 2.8, 'C4': 2.6, 'F1': 2.3, 'F2': 2.5, 'F3': 2.9}
IMPLEMENTED = ["M3", "M6", "M7", "M11"]
WAVE_SHIFT = {
    "T2": {'A3': 0.55, 'A4': 0.15, 'R3': 0.45, 'F2': 0.35, 'F1': 0.2, 'R4': 0.05},
    "T3": {'A3': 0.9, 'A4': 0.3, 'R3': 0.75, 'R4': 0.65, 'F1': 0.7, 'F2': 0.75, 'F3': 0.4, 'R2': 0.3,
           'C1': 0.25, 'C4': -0.45},
}
REACH = {"T2": {"M3": 0.8, "M6": 0.65, "M7": 0.35, "M11": 0.7},
         "T3": {"M3": 0.85, "M6": 0.8, "M7": 0.75, "M11": 0.8}}
EXPOSED_BOOST = 0.35
LEADER_SHIFT = {'A1': 1.0, 'A3': 1.1, 'F1': 1.2, 'F2': 1.0, 'A2': 0.6, 'R4': 0.5, 'C1': 0.4}


def clamp(x):
    return max(1, min(5, int(round(x))))


def row_for(rng, campaign, wave, audience, n_idx):
    leader = audience == "leader"
    person = rng.gauss(0, 0.4)
    exposed = {}
    if wave in REACH:
        for m in IMPLEMENTED:
            exposed[m] = 1 if rng.random() < REACH[wave][m] else 0
    target_boost = {}
    for x in INST.exposure_items:
        if x["module"] in exposed and exposed[x["module"]]:
            for t in x["targets"]:
                target_boost[t] = target_boost.get(t, 0) + EXPOSED_BOOST
    shift = WAVE_SHIFT.get(wave, {})
    adopt_bonus = {"T1": 0, "T2": 0.4, "T3": 0.8}[wave]
    r = {"response_id": f"{campaign}-{n_idx:03d}", "campaign": campaign, "engagement": "DEMO", "wave": wave,
         "audience": audience, "submitted_date": {"T1": "2026-10-01", "T2": "2026-12-10", "T3": "2027-05-20"}[wave],
         "consent_research": 1 if rng.random() < 0.8 else 0,
         "role": "LEAD" if leader else rng.choices(["IC", "MGR", "SL"], [70, 20, 10])[0],
         "use_freq": min(5, rng.choices([1, 2, 3, 4, 5], [8, 22, 30, 25, 15])[0] + (1 if rng.random() < adopt_bonus / 2 else 0)),
         "depth": min(1.0, rng.choice([0, 0.25, 0.25, 0.5, 0.5, 0.75]) + (0.25 if rng.random() < adopt_bonus / 2 else 0)),
         "verify_share": max(0.0, rng.choice([0.25, 0.25, 0.5, 0.5, 0.75, 0.25]) - (0.25 if rng.random() < adopt_bonus / 2 else 0)),
         "error_seen": rng.choices([1, 0], [25, 75])[0],
         "train_hrs": rng.choices([0, 1.5, 3.5, 7, 12], [30, 35, 20, 10, 5] if wave == "T1" else [5, 15, 25, 35, 20])[0],
         "own_time_hrs": rng.choices([0, 3, 8, 15, 25], [35, 35, 18, 8, 4] if wave == "T1" else [55, 30, 10, 4, 1])[0],
         "shadow_ai": rng.choices([1, 0], [40, 60] if wave == "T1" else [25, 75])[0]}
    for d in INST.dimensions:
        mu_d = BASE[d.code] + shift.get(d.code, 0) + target_boost.get(d.code, 0) + (LEADER_SHIFT.get(d.code, 0.3) if leader else 0)
        for it in d.items:
            x = clamp(mu_d + person + rng.gauss(0, 0.6))
            r[it.id] = 6 - x if it.reverse else x
    for x in INST.exposure_items:
        r[x["id"]] = exposed.get(x["module"], "") if wave in REACH else ""
    for x in INST.change_items:
        if wave == "T3":
            base = {"P1": 0.8, "P2": 0.6, "P3": 0.3, "P4": 0.7, "P5": 0.2}[x["id"]]
            r[x["id"]] = max(-2, min(2, int(round(base + rng.gauss(0, 0.9)))))
        else:
            r[x["id"]] = ""
    for x in INST.leadership_items:
        if not leader:
            r[x["id"]] = ""
        elif x["type"] == "likert":
            base = {"L1": 3.2, "L2": 2.6, "L3": 3.4, "L4": 3.6, "L5": 2.8, "L6": 3.0}[x["id"]] + (0.6 if wave == "T3" else 0)
            r[x["id"]] = clamp(base + rng.gauss(0, 0.7))
        else:
            r[x["id"]] = rng.choices([1, 2, 3, 4, ""], [15, 40, 30, 5, 10])[0]
    r["open_text"] = ""
    return r


def write(name, rows):
    with open(OUT / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=INST.columns)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in INST.columns})


def main():
    rng = random.Random(42)
    # T1 staff: keep the workbook's 40 responses, add the new columns.
    t1 = list(csv.DictReader(open(OUT / "demo_responses.csv")))
    for r in t1:
        r.update({"engagement": "DEMO", "wave": "T1", "audience": "staff"})
    write("demo_responses.csv", t1)
    write("demo_T1_leaders.csv", [row_for(rng, "DEMO-T1-LEAD", "T1", "leader", i) for i in range(1, 7)])
    write("demo_T2_staff.csv", [row_for(rng, "DEMO-T2-STAFF", "T2", "staff", i) for i in range(1, 43)])
    write("demo_T3_staff.csv", [row_for(rng, "DEMO-T3-STAFF", "T3", "staff", i) for i in range(1, 45)])
    write("demo_T3_leaders.csv", [row_for(rng, "DEMO-T3-LEAD", "T3", "leader", i) for i in range(1, 6)])
    print("Wrote demo engagement files to data/demo/")


if __name__ == "__main__":
    main()
