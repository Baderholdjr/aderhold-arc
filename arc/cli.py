"""Command line entry point.

    python -m arc run --source sheets                 # production: read the private Google Sheet
    python -m arc run --source csv --path data/demo   # local or imported CSV exports
    python -m arc build-collector                     # regenerate collector/Items.gs from items.yaml
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from . import benchmark, report, roi, sources, waves
from .instrument import ROOT, load
from .scoring import clean, item_means, score_campaign


def _campaign_cfg(code: str) -> dict:
    p = ROOT / "campaigns" / f"{code}.yaml"
    return yaml.safe_load(p.read_text()) if p.exists() else {}


def _engagement_cfg(code: str, cleaned) -> dict:
    """engagements/<CODE>.yaml, else the campaign file of the engagement's first T1 staff campaign."""
    p = ROOT / "engagements" / f"{code}.yaml"
    if p.exists():
        return yaml.safe_load(p.read_text()) or {}
    sub = cleaned[(cleaned["engagement"] == code) & (cleaned["wave"] == "T1") & (cleaned["audience"] == "staff")]
    for c in sorted(sub["campaign"].unique()):
        cfg = _campaign_cfg(c)
        if cfg:
            return cfg
    return {}


def run(args) -> int:
    inst = load()
    if args.source == "sheets":
        df = sources.from_google_sheet(inst)
    else:
        df = sources.from_csv(args.path, inst)
    cleaned = clean(df, inst)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    prev_bench = None
    bench_path = Path(args.benchmark)
    if bench_path.exists():
        prev_bench = json.loads(bench_path.read_text())

    scores, summary = [], []
    for code in sorted(cleaned["campaign"].dropna().unique()):
        if args.campaign and code != args.campaign.upper():
            continue
        s = score_campaign(cleaned, inst, code)
        scores.append(s)
        cfg = _campaign_cfg(code)
        client = cfg.get("client", code)
        r = None
        if not s.suppressed and cfg.get("roi") is not None:
            sub = cleaned[cleaned["campaign"] == code]
            c13 = item_means(sub, inst, None).get("C1.3")
            try:
                r = roi.compute(s.behavioral, (c13 / 5) if c13 else None, cfg.get("roi"))
            except ValueError as exc:
                print(f"[{code}] ROI skipped: {exc}", file=sys.stderr)
        folder = out / code
        folder.mkdir(exist_ok=True)
        report.to_json(s, r, folder / "scorecard.json")
        report.to_html(s, r, client, prev_bench, folder / "report.html")
        report.to_xlsx(s, r, client, folder / "scorecard.xlsx")
        summary.append(f"| {code} | {s.n} | {'yes' if s.suppressed else 'no'} | "
                       f"{'' if s.overall_index is None else round(s.overall_index)} |")

    eng_summary = []
    for eng in sorted(cleaned["engagement"].dropna().unique()):
        if args.campaign:
            break
        sub = cleaned[cleaned["engagement"] == eng]
        if sub[["wave", "audience"]].drop_duplicates().shape[0] < 2:
            continue  # a single baseline staff campaign: the campaign report covers it
        cfg = _engagement_cfg(eng, cleaned)
        ea = waves.analyze(cleaned, inst, eng, cfg.get("roi"))
        folder = out / f"ENGAGEMENT-{eng}"
        folder.mkdir(exist_ok=True)
        report.engagement_to_json(ea, folder / "engagement.json")
        report.engagement_to_html(ea, cfg.get("client", eng), inst, folder / "engagement.html")
        latest = next((c for c in reversed(ea.comparisons) if c.audience == "staff" and c.from_wave == "T1"), None)
        eng_summary.append(f"| {eng} | {', '.join(ea.groups)} | "
                           + (f"{latest.from_wave}→{latest.to_wave}: {latest.summary['Improved']} improved, "
                              f"{latest.summary['Declined']} declined" if latest else "-") + " |")

    bench = benchmark.build(scores, df, inst)
    bench_path.parent.mkdir(parents=True, exist_ok=True)
    bench_path.write_text(json.dumps(bench, indent=2, default=float))

    md = ["| Campaign | Responses | Suppressed | Overall index |", "| --- | --- | --- | --- |", *summary,
          *(["", "| Engagement | Groups | Change |", "| --- | --- | --- |", *eng_summary] if eng_summary else []),
          "", f"Benchmark: {bench['campaigns_included']} client campaigns, "
          f"{bench['respondents_pooled_with_consent']} consented responses pooled."]
    (out / "SUMMARY.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


def build_collector(_args) -> int:
    from tools.build_collector import main as build  # noqa: WPS433
    build()
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="arc", description="Aderhold A.R.C. scoring engine")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="Score all campaigns, write reports and benchmark")
    r.add_argument("--source", choices=["sheets", "csv"], default="csv")
    r.add_argument("--path", default="data/demo", help="CSV file or folder (for --source csv)")
    r.add_argument("--campaign", help="Only this campaign code")
    r.add_argument("--out", default="reports")
    r.add_argument("--benchmark", default="benchmark/summary.json")
    r.set_defaults(func=run)
    b = sub.add_parser("build-collector", help="Regenerate collector/Items.gs from instrument/items.yaml")
    b.set_defaults(func=build_collector)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
