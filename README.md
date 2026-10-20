# Aderhold A.R.C.

**Acceptance · Reliance · Collaboration**: a research-based diagnostic of the human side of AI adoption.
This repository is the operating system for the Aderhold A.R.C. consulting practice. It covers the survey instrument, the automated data collection, the scoring engine, client reports, the cross-client benchmark and the validation statistics.

> Proprietary and confidential. © 2026 Bernard A. Aderhold Jr. All rights reserved. See [LICENSE](LICENSE).

## How it works

```
Client survey link ──► Survey page (Google Apps Script) ──► Private Google Sheet
   …/exec?code=ACME-2026Q4   anonymous, consent, 12 min         one row per response
                                                                       │
                              GitHub Actions, nightly (or on demand) ◄─┘
                                       │
          ┌────────────────────────────┼─────────────────────────────┐
          ▼                            ▼                             ▼
  Client reports per campaign   Benchmark across clients     Validation statistics
  HTML readout, Excel scorecard, (aggregates only, committed  Cronbach's alpha, item-total,
  JSON (private artifacts)       to benchmark/summary.json)   parallel analysis, EFA at n≥200
          +
  Progress report per engagement
  T1 → T2 → T3 change, recommendation check,
  leaders vs. staff, value recovered
```

**Three waves, two audiences.** An engagement measures at **T1 Baseline**, **T2 Midpoint** (after recommendations go live, to adjust course) and **T3 Follow-up** (did it work?), for **staff** and **leaders**. The leadership version rewords the 45 statements about the organization and adds leadership questions. Waves are compared at group level only; nobody is tracked between waves. A dimension is *Improved* or *Declined* only with a move of 5+ points and p < 0.05.

* **One source of truth.** [`instrument/items.yaml`](instrument/items.yaml) defines the 15 gap dimensions, 45 items, 8 behavioral questions and scoring bands. The survey page, Sheet columns, engine and reports are all generated from it.
* **Anonymity by design.** The page stores no names, emails, IP addresses or exact timestamps. Results for groups under 5 are suppressed. Respondent-level data stays in the private Google Sheet and is never committed here. See [docs/DATA_PROTECTION.md](docs/DATA_PROTECTION.md).
* **Same math as the playbook and workbook.** The tests reproduce the Excel workbook's values exactly, including the ROI model.

## Repository map

| Path | What it is |
| --- | --- |
| `instrument/items.yaml` | Instrument v1.1.0: dimensions, items (staff and leader wording), reverse coding, behavioral items, exposure, change and leadership modules, scoring and change rules |
| `collector/` | Google Apps Script survey: `Code.gs` (server), `Survey.html` (page), `Items.gs` (generated), `appsscript.json` |
| `arc/` | Python engine: `scoring`, `waves`, `roi`, `psychometrics`, `benchmark`, `report`, `sources`, `cli` |
| `engagements/` | One YAML per client engagement (client, wave dates, implemented modules, ROI inputs). Start from `_TEMPLATE.yaml` |
| `campaigns/` | Optional YAML for a one-off campaign (ROI inputs). Start from `_TEMPLATE.yaml` |
| `benchmark/summary.json` | Aggregate benchmark, refreshed nightly (no respondent data) |
| `data/demo/` | Synthetic demo engagement: the workbook's 40 baseline responses plus T2, T3 and leadership waves (`tools/make_demo.py`) |
| `.github/workflows/` | `ci.yml` (tests on every push), `nightly.yml` (pull, score, report) |
| `docs/SETUP.md` | One-time setup: Google Sheet, survey deployment, service account, GitHub secrets |

## Everyday use

1. **New engagement.** Copy `engagements/_TEMPLATE.yaml` to `engagements/<ENGAGEMENT>.yaml` and fill in the ROI inputs. In the Sheet's **Campaigns** tab add one row per link (for example `ACME-T1-STAFF` and `ACME-T1-LEAD`) with `active = TRUE`, the engagement code, wave and audience.
2. **Send the links.** `<web app URL>?code=<CODE>`.
3. **Watch results.** The nightly run (or **Actions → Nightly scoring → Run workflow**) scores every campaign and engagement. Download the reports from the run's **Artifacts**.
4. **Midpoint and follow-up.** Add `T2` and `T3` rows, listing the implemented recommendations in `modules`. Close each wave with `active = FALSE`.

Codes starting with `DEMO` or `TEST` are excluded from the benchmark.

## Run locally

```bash
pip install -r requirements-dev.txt
python -m pytest -q                              # tests
node tests/collector.test.js                     # Apps Script logic against a fake Sheet
python -m arc run --source csv --path data/demo  # demo reports in ./reports
python -m arc build-collector                    # after editing items.yaml
```

## Changing the instrument

Edit `instrument/items.yaml`, bump `instrument.version`, run `python -m arc build-collector`, and paste the new `Items.gs` into Apps Script. Do not change item ids, or responses can no longer be compared with the benchmark. Running `setup` after a version change moves old responses to their own tab (see SETUP).

## Manual

The user manual (product guide, training guide, troubleshooting guide) is in [`docs/manual/`](docs/manual/). Edit `docs/manual/manual.md`, then run `python tools/build_manual.py` to rebuild `index.html`.

## License

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/) — free for noncommercial use; commercial use by arrangement. © 2025–2026 Bernard A. Aderhold Jr.
