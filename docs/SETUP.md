# One-time setup (about 30 minutes)

You need a Google account and this GitHub repository. Everything uses free tiers.

## 1. Create the private response Sheet

1. In Google Drive, create a new Google Sheet named **Aderhold A.R.C. Responses**. Keep it private; do not share it with clients.
2. Copy its ID from the URL: `https://docs.google.com/spreadsheets/d/`**`THIS_PART`**`/edit`. You will need it in step 4.

## 2. Install the survey (Apps Script)

1. In the Sheet: **Extensions → Apps Script**.
2. Create these files and paste in the contents from the repo's `collector/` folder:
   * `Code.gs`: replace the default file's contents.
   * `Items.gs`: **+ → Script**, name it `Items`.
   * `Survey.html`: **+ → HTML**, name it `Survey`.
3. **Project Settings (gear icon) → Show "appsscript.json" manifest file**. Then replace `appsscript.json` with `collector/appsscript.json`.
4. Select the function **setup** in the toolbar and click **Run**. Approve the permission prompt; the script only gets access to this one spreadsheet. This creates the **Responses** and **Campaigns** tabs and four test campaigns: `TEST-0001` (staff baseline), `TEST-LEAD` (leadership survey), `TEST-T2` (midpoint) and `TEST-T3` (follow-up).
5. **Deploy → New deployment → type: Web app**.
   * Execute as: **Me**
   * Who has access: **Anyone**. Respondents don't sign in, which keeps the survey anonymous.
   * Click **Deploy** and copy the **Web app URL**.
6. Test it: open `<Web app URL>?code=TEST-0001`, complete the survey, and check that a row appears in **Responses**. Then open `?code=TEST-LEAD`, `?code=TEST-T2` and `?code=TEST-T3` to see the other versions.

> When you later update `Survey.html`, `Code.gs` or `Items.gs`: **Deploy → Manage deployments → edit (pencil) → Version: New version → Deploy**. The URL stays the same.

## 3. Create a read-only service account for GitHub

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create a project named `aderhold-arc`.
2. **APIs & Services → Library**: enable the **Google Sheets API**.
3. **IAM & Admin → Service Accounts → Create service account**, named `arc-reader`. Skip the role assignments.
4. Open the new account: **Keys → Add key → Create new key → JSON**. A `.json` file downloads.
   Treat it like a password. Never commit it to the repo.
5. Copy the service account's email (`arc-reader@…iam.gserviceaccount.com`). Share the Google Sheet with it as **Viewer**.

## 4. Add the GitHub secrets

In this repo: **Settings → Secrets and variables → Actions → New repository secret**.

| Name | Value |
| --- | --- |
| `ARC_SHEET_ID` | The Sheet ID from step 1 |
| `GOOGLE_SERVICE_ACCOUNT` | The entire contents of the JSON key file from step 3 |

Then delete the downloaded key file from your computer, or store it in a password manager.

## 5. First run

**Actions → Nightly scoring → Run workflow.** When it finishes, open the run. The **Summary** shows each campaign's response count, and **Artifacts** holds the reports (`report.html`, `scorecard.xlsx`, `scorecard.json` per campaign).

From then on it runs every night at about 3:17 a.m. Pacific.

## Running a client engagement

An engagement has up to three waves (T1 baseline, T2 midpoint, T3 follow-up) and two audiences (staff and leaders). Each wave/audience pair is one campaign, with its own link.

| Campaigns column | Example | Meaning |
| --- | --- | --- |
| `code` | `ACME-T1-STAFF` | The link code: letters, digits and dashes |
| `display_name` | `Acme` | Shown on the survey header |
| `active` | `TRUE` | Accepts answers while TRUE |
| `notes` | | Free text |
| `engagement` | `ACME` | Same value for every campaign of the engagement (blank = the code) |
| `wave` | `T1`, `T2` or `T3` | Blank = T1 |
| `audience` | `staff` or `leader` | Blank = staff |
| `modules` | `M3, M6, M7` | T2/T3 only: recommendations implemented; drives the exposure questions |

1. **Baseline:** add `ACME-T1-STAFF` and `ACME-T1-LEAD`. Copy `engagements/_TEMPLATE.yaml` to `engagements/ACME.yaml` and fill in the ROI inputs.
2. Send each link (`<Web app URL>?code=ACME-T1-STAFF`) through the client's sponsor, explaining the purpose and the anonymity rules. Leader results are reported at 3+ responses, staff at 5+.
3. **Midpoint**, 6–10 weeks after recommendations go live: add `ACME-T2-STAFF` with wave `T2` and the implemented modules.
4. **Follow-up**, 3–6 months after T1: add `ACME-T3-STAFF` and `ACME-T3-LEAD` with wave `T3` and the modules.
5. Close each wave by setting `active = FALSE`.

Each campaign gets its own report; the engagement gets a progress report (`ENGAGEMENT-ACME/engagement.html`) once it has two or more groups.

A one-off diagnostic is still a single campaign (for example `ACME-2026Q4`) with `campaigns/ACME-2026Q4.yaml`.

## Upgrading from v1.0 to v1.1

1. In Apps Script, replace `Code.gs`, `Items` and `Survey` with the current files from `collector/`. Save.
2. Run **setup**. It renames the existing Responses tab to `Responses v1.0.0`, starts a new Responses tab, adds the four new Campaigns columns and the new test campaigns. Existing campaign rows keep working as staff baselines.
3. **Deploy → Manage deployments → pencil → Version: New version → Deploy.**
4. Test `?code=TEST-LEAD`, `?code=TEST-T2` and `?code=TEST-T3`.

The nightly run reads both the new and the earlier-version tabs.

## Changing the instrument version

Responses from different instrument versions must not mix. After pasting a new `Items.gs`, run **setup**: it moves the existing responses to a tab named after their version (for example `Responses v1.1.0`) and starts a fresh Responses tab. Don't rename or delete those tabs; the nightly run reads every tab named `Responses` or `Responses v…`. Item ids that stay the same remain comparable in the benchmark. Avoid changing the instrument in the middle of an engagement.

## Troubleshooting

| What you see | Cause | Fix |
| --- | --- | --- |
| "Sorry, unable to open the file at this time. Please check the address and try again." | A known Google issue when the browser is signed into **more than one Google account**. It can also mean the URL is malformed, or the deployment was archived. | Open the link in a **private/incognito window**. Respondents are usually signed into one account or none, so they won't see this. Copy the exact link printed by `checkSetup()`. |
| Same message even in incognito, with the correct `/exec` link, and the script owned by a **Google Workspace** (company domain) account | The Workspace admin setting that blocks sharing outside the organization also blocks anonymous web-app access | Admin console: **Apps → Google Workspace → Drive and Docs → Sharing settings → Sharing options** → allow sharing outside the organization. This can take up to 24 hours (usually minutes). Or own the Sheet and script with a personal Gmail account instead. |
| "Sorry, unable to open the file" only when the link has a `?c=` parameter | Google reserves the URL parameters `c` and `sid` for Apps Script itself | Use `?code=` (the survey reads `code`). |
| "This survey link is not active" | The link has no `?code=CODE`, the code isn't in the Campaigns tab, or the campaign is set inactive | The page states which one. Run `checkSetup()` and read the execution log. |
| Changes don't appear | The deployment still points to an old version | **Deploy → Manage deployments → pencil → Version: New version → Deploy** |
| Nightly run says secrets are not set | `ARC_SHEET_ID` / `GOOGLE_SERVICE_ACCOUNT` are missing | Step 4 above |
| Nightly run fails with a permission error | The Sheet isn't shared with the service account email | Share the Sheet with it as Viewer |
| T2/T3 survey has no "What has changed" page | `wave` blank or `modules` blank/misspelled | Set `wave` and list modules as `M3, M6`; check with `checkSetup()` |
| No progress report | The engagement's campaigns have different `engagement` values, or only one group has responses | Use the same `engagement` value on every row |
| Leader report suppressed | Fewer than 3 leader responses | Collect more, or interview leaders instead |
