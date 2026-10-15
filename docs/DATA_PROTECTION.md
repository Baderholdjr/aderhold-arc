# Data protection

Candid answers are the product. People only answer candidly if anonymity is real, so these rules are built into the system, not left to policy.

## What is collected

| Collected | Not collected |
| --- | --- |
| Random response id, campaign code, submission **date** (UTC, no time) | Name, email, employee id |
| Role group (IC / manager / senior leader, or leader on the leadership survey), campaign wave and audience | IP address, device or browser details |
| 45 agreement answers, 7 behavioral answers, one optional comment; at midpoint and follow-up, yes/no answers on which changes reached them and five "looking back" ratings; for leaders, seven leadership answers | Exact timestamp, location |
| Research-consent flag (optional, separate from taking part) | Sign-in identity (the survey needs no login) |

Comments are capped at 1,000 characters, and respondents are asked not to include names. Text that could execute as a spreadsheet formula is neutralized.

## Where data lives

* **Respondent-level data** lives only in the private Google Sheet owned by Dr. Aderhold. GitHub Actions reads it with a read-only service account and holds it in memory during the run. It is never written to the repository.
* **Client reports** contain group aggregates only. They are stored as private workflow artifacts and deleted after 30 days. Download them and deliver them to the client through your normal secure channel.
* **The benchmark** (`benchmark/summary.json`) holds only campaign-level and pooled statistics.

## Reporting rules

* Groups with fewer than **5** respondents are suppressed everywhere: the whole campaign, the IC group and the leaders group.
* **Leadership survey** campaigns are reported at **3** or more respondents, because leadership groups are small. Leaders are told this before they start and asked to keep identifying details out of comments. Review leader comments with extra care; don't quote them if the group is under 5.
* **Waves are linked at group level only.** No identifier follows a person from the baseline to the follow-up survey, so no individual's change can be tracked.
* Comments are reviewed by the consultant before any are quoted, and potentially identifying details are removed.
* Clients never receive the raw Sheet.

## Research use

The benchmark and validation statistics pool only responses with `consent_research = 1`. If results will be published (for example, a validation paper), confirm whether an IRB review is required for the secondary analysis. Keep the consent wording in `collector/Survey.html` aligned with that review.

## Contracts

Each client engagement should include a data-processing clause covering: purpose limitation, the anonymity rules above, retention (raw responses deleted 12 months after the final readout unless the client agrees otherwise), and consent to include anonymized aggregates in the A.R.C. benchmark.
