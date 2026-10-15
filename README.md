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
```

* **One source of truth.** [`instrument/items.yaml`](instrument/items.yaml) defines the 15 gap dimensions, 45 items, 8 behavioral questions and scoring bands. The survey page, Sheet columns, engine and reports are all generated from it.
* **Anonymity by design.** The page stores no names, emails, IP addresses or exact timestamps. Results for groups under 5 are suppressed. Respondent-level data stays in the private Google Sheet and is never committed here. See [docs/DATA_PROTECTION.md](docs/DATA_PROTECTION.md).
* **Same math as the playbook and workbook.** The tests reproduce the Excel workbook's values exactly, including the ROI model.

## Repository map

| Path | What it is |
| --- | --- |
| `instrument/items.yaml` | Instrument v1.0.0: dimensions, items, reverse coding, behavioral items, scoring bands |
| `collector/` | Google Apps Script survey: `Code.gs` (server), `Survey.html` (page), `Items.gs` (generated), `appsscript.json` |
| `arc/` | Python engine: `scoring`, `roi`, `psychometrics`, `benchmark`, `report`, `sources`, `cli` |
| `campaigns/` | One YAML per client survey wave (client name, survey dates, ROI inputs). Start from `_TEMPLATE.yaml` |
| `benchmark/summary.json` | Aggregate benchmark, refreshed nightly (no respondent data) |
| `data/demo/` | Synthetic demo responses (the same set as the Excel workbook) |
| `.github/workflows/` | `ci.yml` (tests on every push), `nightly.yml` (pull, score, report) |
| `docs/SETUP.md` | One-time setup: Google Sheet, survey deployment, service account, GitHub secrets |

## Everyday use

1. **New client wave.** Copy `campaigns/_TEMPLATE.yaml` to `campaigns/<CODE>.yaml` and fill in the ROI inputs. Add the same code to the **Campaigns** tab of the Sheet with `active = TRUE`.
2. **Send the link.** `<web app URL>?code=<CODE>`.
3. **Watch results.** The nightly run (or **Actions → Nightly scoring → Run workflow**) scores every campaign. Download the reports from the run's **Artifacts**.
4. **Close the wave.** Set `active = FALSE` in the Campaigns tab.

Codes starting with `DEMO` or `TEST` are excluded from the benchmark.

## Run locally

```bash
pip install -r requirements-dev.txt
python -m pytest -q                              # tests
python -m arc run --source csv --path data/demo  # demo reports in ./reports
python -m arc build-collector                    # after editing items.yaml
```

## Changing the instrument

Edit `instrument/items.yaml`, bump `instrument.version`, run `python -m arc build-collector`, and paste the new `Items.gs` into Apps Script. Do not change item ids, or responses can no longer be compared with the benchmark. A new version needs a new Responses tab (see SETUP).
