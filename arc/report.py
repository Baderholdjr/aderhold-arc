"""Client reports: scorecard JSON, a self-contained HTML readout and an Excel scorecard.

Reports contain aggregates only (groups of 5+). They are written to an output folder
that is git-ignored; the nightly workflow uploads them as private workflow artifacts.
"""
from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from .benchmark import percentile_rank
from .roi import RoiResult
from .scoring import CampaignScore

CSS = """body{font-family:Arial,Helvetica,sans-serif;color:#1d2733;max-width:1080px;margin:32px auto;padding:0 16px;line-height:1.45}
h1{font-size:26px;margin:0} h2{font-size:19px;margin-top:32px;border-bottom:2px solid #1f3a5f;padding-bottom:4px}
.sub{color:#5b6b7c} table{border-collapse:collapse;width:100%;font-size:13px}
th{background:#1f3a5f;color:#fff;text-align:left;padding:6px} td{padding:5px 6px;border-bottom:1px solid #e3e7ec}
.pills{display:flex;gap:12px;flex-wrap:wrap} .pill{flex:1;min-width:180px;border:1px solid #cfd7e0;border-radius:8px;padding:12px}
.pn{font-weight:700} .pv{font-size:30px;font-weight:700;color:#1f3a5f} .pl{color:#5b6b7c;font-size:13px}
.wf{display:flex;align-items:center;gap:8px;font-size:13px;margin:4px 0} .wl{width:170px;flex:none}
.track{position:relative;flex:1;height:18px} .wfbox .bar{position:absolute;top:1px;height:16px} .wv{position:absolute;top:0;white-space:nowrap}
.total{background:#9aa5b1} .lost{background:#e6a19a}
.kv td:first-child{width:60%} .note{color:#5b6b7c;font-size:12px} .warn{color:#c0392b;font-weight:700}
.up{color:#1e8449;font-weight:700} .down{color:#c0392b;font-weight:700} .flat{color:#5b6b7c}
.tag{display:inline-block;padding:1px 8px;border-radius:10px;font-size:12px;font-weight:600}
.t-good{background:#e3f4e8;color:#1e6b3a} .t-bad{background:#fbe5e2;color:#9b2c1f} .t-mid{background:#fdf2dc;color:#8a5a12} .t-none{background:#eef1f4;color:#4b5965}
"""

SEV_COLOR = {"Critical": "#c0392b", "Significant": "#d68910", "Moderate": "#b7950b", "Healthy": "#1e8449"}


def _f(v, digits=0, pct=False, money=False):
    if v is None:
        return "n<5" if not money else "-"
    if pct:
        return f"{v * 100:.{digits}f}%"
    if money:
        return f"${v:,.0f}"
    return f"{v:.{digits}f}"


def _cell_bg(v):
    if v is None:
        return "#f2f2f2"
    # red (20) -> amber (60) -> green (90)
    t = max(0.0, min(1.0, (v - 20) / 70))
    if t < 4 / 7:
        u = t / (4 / 7)
        r, g, b = 248 + (255 - 248) * u, 105 + (235 - 105) * u, 107 + (132 - 107) * u
    else:
        u = (t - 4 / 7) / (3 / 7)
        r, g, b = 255 + (99 - 255) * u, 235 + (190 - 235) * u, 132 + (123 - 132) * u
    return f"rgb({int(r)},{int(g)},{int(b)})"


def to_json(score: CampaignScore, roi: RoiResult | None, path: Path) -> None:
    payload = {"generated": date.today().isoformat(), "score": score.to_dict(),
               "roi": roi.to_dict() if roi else None}
    path.write_text(json.dumps(payload, indent=2))


def to_html(score: CampaignScore, roi: RoiResult | None, client: str, bench: dict | None, path: Path) -> None:
    e = html.escape
    staff = score.audience == "staff"
    rows = []
    for d in score.dimensions:
        pos = percentile_rank(d.index_all, d.code, bench) or ""
        sev = d.severity or ""
        rows.append(
            f"<tr><td>{e(d.code)}</td><td>{e(d.name)}</td><td>{e(d.pillar)}</td>"
            f"<td style='background:{_cell_bg(d.index_all)}'>{_f(d.index_all)}</td>"
            + (f"<td style='background:{_cell_bg(d.index_ic)}'>{_f(d.index_ic)}</td>"
               f"<td style='background:{_cell_bg(d.index_leaders)}'>{_f(d.index_leaders)}</td>"
               f"<td>{_f(d.perception_gap) if d.perception_gap is not None else ''}</td>" if staff else "") +
            f"<td style='color:{SEV_COLOR.get(sev, '#333')};font-weight:600'>{e(sev)}</td>"
            f"<td>{e(d.flag or '')}</td><td>{e(pos)}</td></tr>")
    pillars = "".join(
        f"<div class='pill'><div class='pn'>{e(p.pillar)}</div><div class='pv'>{_f(p.index_all)}</div>"
        f"<div class='pl'>Level {p.level or '-'}: {e(p.level_name or '')}</div></div>" for p in score.pillars)
    gaps = "".join(f"<li><b>{e(g['code'])} {e(g['name'])}</b>: {_f(g['index'])} ({e(g['severity'] or '')})</li>"
                   for g in score.top_gaps)
    b = score.behavioral or {}
    beh = [("Active adoption (weekly or more)", _f(b.get("active_adoption"), pct=True)),
           ("Depth of use", _f(b.get("depth_of_use"), pct=True)),
           ("Share of saved time spent re-checking", _f(b.get("verification_share"), pct=True)),
           ("Saw an AI error reach output (90 days)", _f(b.get("error_seen_90d"), pct=True)),
           ("Average AI training hours (12 months)", _f(b.get("training_hours_avg"), 1)),
           ("Under 5 hours of training", _f(b.get("share_under_5_training_hours"), pct=True)),
           ("Own-time learning hours (3 months)", _f(b.get("own_time_hours_avg"), 1)),
           ("Used unapproved AI tools (30 days)", _f(b.get("shadow_ai_30d"), pct=True))]
    beh_html = "".join(f"<tr><td>{e(k)}</td><td>{v}</td></tr>" for k, v in beh)

    roi_html = ""
    if roi:
        mx = (roi.achievable_value or 1) / 0.8  # bars use at most 80% of the track; labels sit to their right
        bars = ""
        for w in roi.waterfall:
            if w["lost"] is None:
                left, width, cls, label = 0.0, w["running"] / mx * 100, "total", _f(w["running"], money=True)
            else:
                left, width, cls, label = w["running"] / mx * 100, w["lost"] / mx * 100, "lost", "-" + _f(w["lost"], money=True)
            bars += (f"<div class='wf'><span class='wl'>{e(w['step'])}</span><span class='track'>"
                     f"<span class='bar {cls}' style='left:{left:.1f}%;width:{width:.1f}%'></span>"
                     f"<span class='wv' style='left:calc({left + width:.1f}% + 6px)'>{label}</span></span></div>")
        roi_html = f"""
<h2>Value leakage</h2>
<p>People-side gaps let through <b>{_f(roi.share_realized, 1, pct=True)}</b> of achievable AI value
({_f(roi.current_value, money=True)} of {_f(roi.achievable_value, money=True)} a year).</p>
<div class='wfbox'>{bars}</div>
<table class='kv'>
<tr><td>Recoverable value per year</td><td><b>{_f(roi.recoverable_value, money=True)}</b></td></tr>
<tr><td>Risk-adjusted (after confidence haircut)</td><td>{_f(roi.risk_adjusted_value, money=True)}</td></tr>
<tr><td>Engagement fee</td><td>{_f(roi.engagement_fee, money=True)}</td></tr>
<tr><td>Net first-year return (unadjusted / risk-adjusted)</td><td>{_f(roi.net_return_x, 1)}x / {_f(roi.net_return_risk_adjusted_x, 1)}x</td></tr>
<tr><td>Payback</td><td>{_f(roi.payback_months, 1)} months</td></tr>
</table>
<p class='note'>Estimates use the client's inputs and survey-derived factors; see the ROI inputs in the campaign file.</p>"""

    supp = (f"<p class='warn'>Fewer than {score.min_group_size} responses: results suppressed to protect anonymity.</p>"
            if score.suppressed else "")
    extra = _modules_html(score)
    who = (f"{score.n} respondents ({score.n_ic} individual contributors, {score.n_leaders} managers and leaders)"
           if staff else f"Leadership survey &middot; {score.n} leaders")
    wave_txt = f" &middot; wave {e(score.wave)}" if score.wave else ""
    head_cols = ("<th>All</th><th>IC</th><th>Leaders</th><th>Gap (pts)</th>" if staff else "<th>Leaders</th>")
    gap_note = (" A perception gap means managers and leaders score the dimension 15+ points above individual "
                "contributors. Groups under 5 are suppressed." if staff else
                " Leadership results are reported only when 3 or more leaders respond.")
    doc = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Aderhold A.R.C. Scorecard: {e(client)}</title>
<style>
{CSS}</style></head><body>
<h1>Aderhold A.R.C. Scorecard</h1>
<div class='sub'>{e(client)} &middot; campaign {e(score.campaign)}{wave_txt} &middot; {who} &middot; instrument v{e(score.instrument_version)} &middot; generated {date.today().isoformat()}</div>
{supp}
<h2>Maturity by pillar</h2><div class='pills'>{pillars}</div>
<p>Overall A.R.C. index: <b>{_f(score.overall_index)}</b> / 100</p>
<h2>Top gaps</h2><ol>{gaps}</ol>
<h2>Gap dimensions</h2>
<table><tr><th>Code</th><th>Dimension</th><th>Pillar</th>{head_cols}<th>Severity</th><th>Flag</th><th>Benchmark</th></tr>
{''.join(rows)}</table>
<p class='note'>Index 0-100. Severity: Critical &lt;40, Significant 40-59, Moderate 60-74, Healthy &ge;75.{gap_note}</p>
<h2>Behavioral signals</h2><table class='kv'>{beh_html}</table>
{extra}
{roi_html}
<p class='note'>Aderhold A.R.C.&trade; research-based diagnostic. Confidential: prepared for {e(client)}.</p>
</body></html>"""
    path.write_text(doc)


def _modules_html(score: CampaignScore) -> str:
    """Exposure check (T2/T3), perceived change (T3) and the leadership module, when present."""
    e = html.escape
    out = ""
    if score.exposure:
        rows = "".join(f"<tr><td>{e(m)}</td><td>{_f(x['reach'], pct=True)}</td><td>{x['answered']}</td>"
                       f"<td>{e(', '.join(x['targets']))}</td></tr>" for m, x in score.exposure.items())
        out += ("<h2>Did the recommendations reach people?</h2><table><tr><th>Module</th><th>Reach (answered Yes)</th>"
                f"<th>Answered</th><th>Targets</th></tr>{rows}</table>"
                "<p class='note'>Reach = share answering Yes among those answering Yes or No. Under 50% means the change is not reaching people yet.</p>")
    if score.change:
        rows = "".join(f"<tr><td>{e(x['text'])}</td><td>{x['mean']:+.2f}</td><td>{_f(x['share_better'], pct=True)}</td>"
                       f"<td>{_f(x['share_worse'], pct=True)}</td></tr>" for x in score.change.values())
        out += ("<h2>Perceived change since the program started</h2><table><tr><th>Item</th><th>Mean (-2 to +2)</th>"
                f"<th>Better</th><th>Worse</th></tr>{rows}</table>")
    if score.leadership:
        rows = ""
        for x in score.leadership.values():
            if "share_agree" in x:
                rows += f"<tr><td>{e(x['text'])}</td><td>{_f(x['share_agree'], pct=True)} agree</td><td>{x['mean']:.1f} / 5</td></tr>"
            else:
                dist = ", ".join(f"{e(k)}: {v}" for k, v in x["counts"].items())
                rows += f"<tr><td>{e(x['text'])}</td><td colspan='2'>{dist}</td></tr>"
        out += f"<h2>Leadership module</h2><table><tr><th>Statement</th><th>Agreement</th><th>Mean</th></tr>{rows}</table>"
    return out


def to_xlsx(score: CampaignScore, roi: RoiResult | None, client: str, path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Scorecard"
    hdr_font, hdr_fill = Font(name="Arial", bold=True, color="FFFFFF"), PatternFill("solid", fgColor="1F3A5F")
    ws.append([f"Aderhold A.R.C. Scorecard: {client} ({score.campaign})"])
    ws["A1"].font = Font(name="Arial", bold=True, size=14)
    ws.append([f"n = {score.n} (IC {score.n_ic}, leaders {score.n_leaders}); instrument v{score.instrument_version}"])
    ws.append([])
    ws.append(["Code", "Dimension", "Pillar", "Index (all)", "Index (IC)", "Index (leaders)", "Perception gap", "Severity", "Flag"])
    for c in ws[4]:
        c.font, c.fill = hdr_font, hdr_fill
    for d in score.dimensions:
        ws.append([d.code, d.name, d.pillar, _r(d.index_all), _r(d.index_ic), _r(d.index_leaders),
                   _r(d.perception_gap), d.severity, d.flag])
    ws.append([])
    ws.append(["Pillar", "Index (all)", "Index (IC)", "Index (leaders)", "Level", "Level name"])
    for c in ws[ws.max_row]:
        c.font, c.fill = hdr_font, hdr_fill
    for p in score.pillars:
        ws.append([p.pillar, _r(p.index_all), _r(p.index_ic), _r(p.index_leaders), p.level, p.level_name])
    ws.append(["Overall", _r(score.overall_index)])
    for col, w in zip("ABCDEFGHI", [10, 36, 14, 12, 12, 14, 14, 12, 16]):
        ws.column_dimensions[col].width = w
    if roi:
        r = wb.create_sheet("Value leakage")
        for k, v in [("Achievable value", roi.achievable_value), ("Current realized value", roi.current_value),
                     ("Target value", roi.target_value), ("Share realized", roi.share_realized),
                     ("Recoverable value per year", roi.recoverable_value), ("Risk-adjusted value", roi.risk_adjusted_value),
                     ("Engagement fee", roi.engagement_fee), ("Net return (x)", roi.net_return_x),
                     ("Net return risk-adjusted (x)", roi.net_return_risk_adjusted_x), ("Payback (months)", roi.payback_months)]:
            r.append([k, v])
        r.column_dimensions["A"].width = 34
        r.column_dimensions["B"].width = 16
    for sheet in wb.worksheets:
        for row in sheet.iter_rows():
            for c in row:
                if c.font.name != "Arial":
                    c.font = Font(name="Arial", bold=c.font.bold, size=c.font.size, color=c.font.color)
    wb.save(path)


def _r(v):
    return None if v is None else round(v, 1)


MODULE_NAMES = {
    "M1": "Why AI, Why Us (leader narrative)", "M2": "Manager as AI Coach", "M3": "Role-Based AI Onboarding",
    "M4": "Use-Case Discovery Lab", "M5": "Know Your AI", "M6": "Proportionate Verification",
    "M7": "When AI Flops (flop protocol)", "M8": "AI Direction Ladder", "M9": "Workflow Redesign Studio",
    "M10": "Apprenticeship in the Age of AI", "M11": "Governance for Leaders", "M12": "Buyer's Explainability Checklist",
}
STATUS_TAG = {"Improved": "t-good", "Working": "t-good", "Declined": "t-bad",
              "Reaching people, moving the wrong way": "t-bad", "Not reaching people": "t-mid",
              "Reaching people, not yet moving": "t-mid"}


def _tag(status: str) -> str:
    return f"<span class='tag {STATUS_TAG.get(status, 't-none')}'>{html.escape(status)}</span>"


def _delta(v) -> str:
    if v is None:
        return ""
    cls = "up" if v >= 5 else "down" if v <= -5 else "flat"
    return f"<span class='{cls}'>{v:+.1f}</span>"


def engagement_to_json(ea, path: Path) -> None:
    path.write_text(json.dumps({"generated": date.today().isoformat(), **ea.to_dict()}, indent=2, default=float))


def engagement_to_html(ea, client: str, inst, path: Path) -> None:
    """Three-wave and leadership comparison report for one engagement."""
    e = html.escape
    waves = [w for w in ("T1", "T2", "T3") if any(k.startswith(w + "/") for k in ea.groups)]
    names = {"T1": "Baseline", "T2": "Midpoint", "T3": "Follow-up"}

    def g(w, a):
        s = ea.groups.get(f"{w}/{a}")
        return s if s and not s.suppressed else None

    # Respondents per group
    cells = ""
    for a in ("staff", "leader"):
        cells += f"<tr><td>{'Staff' if a == 'staff' else 'Leaders'}</td>"
        for w in waves:
            s = ea.groups.get(f"{w}/{a}")
            cells += f"<td>{'' if not s else (str(s.n) + (' (suppressed)' if s.suppressed else ''))}</td>"
        cells += "</tr>"
    wave_head = "".join(f"<th>{w} {names[w]}</th>" for w in waves)
    sections = [f"<h2>Who answered</h2><table><tr><th>Group</th>{wave_head}</tr>{cells}</table>"]

    # Pillar trend
    rows = ""
    for a in ("staff", "leader"):
        if not any(g(w, a) for w in waves):
            continue
        for i, p in enumerate(inst.pillars):
            rows += f"<tr><td>{'Staff' if a == 'staff' else 'Leaders'}</td><td>{e(p)}</td>"
            for w in waves:
                s = g(w, a)
                ps = s.pillars[i] if s else None
                rows += (f"<td style='background:{_cell_bg(ps.index_all)}'>{_f(ps.index_all)} "
                         f"<span class='note'>L{ps.level}</span></td>" if ps and ps.index_all is not None else "<td></td>")
            rows += "</tr>"
    sections.append(f"<h2>Maturity by pillar, wave by wave</h2><table><tr><th>Group</th><th>Pillar</th>{wave_head}</tr>{rows}</table>"
                    "<p class='note'>Index 0-100; L = maturity level (1 Imposed to 5 Integrated).</p>")

    # Dimension change (staff): T1 vs latest
    staff_comps = [c for c in ea.comparisons if c.audience == "staff"]
    main = next((c for c in staff_comps if c.from_wave == "T1" and c.to_wave == "T3"), None) or \
        next((c for c in staff_comps if c.from_wave == "T1"), None)
    if main:
        mid = next((c for c in staff_comps if c.from_wave == "T2" and c.to_wave == "T3"), None)
        by_code = {r["code"]: r for r in (mid.rows if mid else [])}
        rows = ""
        for r in main.rows:
            vals = "".join(f"<td>{_f(next(d.index_all for d in g(w, 'staff').dimensions if d.code == r['code']))}</td>"
                           if g(w, "staff") else "<td></td>" for w in waves)
            p = "" if r["p"] is None else ("&lt;0.001" if r["p"] < 0.001 else f"{r['p']:.3f}")
            rows += (f"<tr><td>{e(r['code'])}</td><td>{e(r['name'])}</td>{vals}<td>{_delta(r['delta'])}</td>"
                     f"<td>{p}</td><td>{_tag(r['status'])}</td>"
                     + (f"<td>{_tag(by_code[r['code']]['status'])}</td>" if mid else "") + "</tr>")
        s = main.summary
        sections.append(
            f"<h2>Change by dimension: {main.from_wave} to {main.to_wave} (staff)</h2>"
            f"<p><b>{s['Improved']}</b> improved, <b>{s['Declined']}</b> declined, <b>{s['No reliable change']}</b> showed no reliable change.</p>"
            f"<table><tr><th>Code</th><th>Dimension</th>{wave_head}<th>Change</th><th>p</th><th>{main.from_wave}→{main.to_wave}</th>"
            + ("<th>T2→T3</th>" if mid else "") + f"</tr>{rows}</table>"
            "<p class='note'>Improved or Declined requires a change of 5+ index points AND p &lt; 0.05 (Welch t-test on "
            "respondent-level scores). Waves are compared as groups; no individual is tracked between waves.</p>")

    # Exposure diagnostics
    for w, diag in ea.exposure.items():
        rows = ""
        for x in diag:
            tch = ", ".join(f"{t} {v:+.1f}" for t, v in x["target_changes"].items()) or "-"
            ed = "" if x["exposed_minus_unexposed"] is None else f"{x['exposed_minus_unexposed']:+.1f}"
            rows += (f"<tr><td>{e(x['module'])} {e(MODULE_NAMES.get(x['module'], ''))}</td><td>{_f(x['reach'], pct=True)}</td>"
                     f"<td>{e(tch)}</td><td>{ed}</td><td>{_tag(x['status'])}</td></tr>")
        sections.append(
            f"<h2>{'Midpoint' if w == 'T2' else 'Follow-up'} check: are the recommendations working? ({w})</h2>"
            "<table><tr><th>Recommendation</th><th>Reached</th><th>Target dimensions since T1</th>"
            f"<th>Exposed minus not exposed</th><th>Status</th></tr>{rows}</table>"
            "<p class='note'>Reached = share of staff saying the change reached them. 'Exposed minus not exposed' compares "
            "target-dimension scores within this wave between people the change reached and people it didn't (shown when "
            "each group has 5+). A change that isn't reaching people needs a delivery fix; one that reaches people but "
            "doesn't move its targets needs a design fix.</p>")

    # Leader vs staff
    for w, gaps in ea.leader_gaps.items():
        rows = "".join(f"<tr><td>{e(x['code'])}</td><td>{e(x['name'])}</td><td>{_f(x['staff'])}</td><td>{_f(x['leader'])}</td>"
                       f"<td>{_gap(x['gap'])}</td><td>{e(x['flag'] or '')}</td></tr>"
                       for x in gaps)
        n_flag = sum(1 for x in gaps if x["flag"])
        sections.append(f"<h2>Leaders vs. staff ({w} {names[w]})</h2><p>{n_flag} of 15 dimensions differ by 15+ points.</p>"
                        f"<table><tr><th>Code</th><th>Dimension</th><th>Staff</th><th>Leaders</th><th>Gap</th><th>Flag</th></tr>{rows}</table>"
                        "<p class='note'>Gap = leadership index minus staff index. Leaders answer the same 15 dimensions, worded from their vantage point.</p>")

    # Perceived change
    for w in waves:
        s = g(w, "staff")
        if s and s.change:
            rows = "".join(f"<tr><td>{e(x['text'])}</td><td>{x['mean']:+.2f}</td><td>{_f(x['share_better'], pct=True)}</td>"
                           f"<td>{_f(x['share_worse'], pct=True)}</td></tr>" for x in s.change.values())
            sections.append(f"<h2>What staff say changed ({w})</h2><table><tr><th>Item</th><th>Mean (-2 to +2)</th>"
                            f"<th>Better</th><th>Worse</th></tr>{rows}</table>")

    # Value recovered
    if ea.value:
        rows = "".join(f"<tr><td>{w} {names[w]}</td><td>{_f(v['realized'], money=True)}</td>"
                       f"<td>{_f(v['share_realized'], 1, pct=True)}</td><td>{_f(v['recovered_vs_T1'], money=True) if w != 'T1' else ''}</td></tr>"
                       for w, v in ea.value.items())
        sections.append("<h2>Value recovered</h2><table><tr><th>Wave</th><th>Realized annual value</th><th>Share of achievable</th>"
                        f"<th>Recovered vs. T1</th></tr>{rows}</table>"
                        "<p class='note'>Each wave uses that wave's survey factors (adoption, depth, verification, capture) with "
                        "the client's inputs held constant. Overrides in the campaign file are ignored here so waves are comparable.</p>")

    group_txt = ", ".join(f"{k} n={v.n}" for k, v in ea.groups.items())
    doc = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Aderhold A.R.C. Progress: {e(client)}</title><style>
{CSS}</style></head><body>
<h1>Aderhold A.R.C. Progress Report</h1>
<div class='sub'>{e(client)} &middot; engagement {e(ea.engagement)} &middot; {e(group_txt)} &middot; generated {date.today().isoformat()}</div>
{''.join(sections)}
<p class='note'>Aderhold A.R.C.&trade; research-based diagnostic. Confidential: prepared for {e(client)}.</p>
</body></html>"""
    path.write_text(doc)


def _gap(v) -> str:
    return "" if v is None else f"{v:+.1f}"
