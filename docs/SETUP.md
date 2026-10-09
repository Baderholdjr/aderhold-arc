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
4. Select the function **setup** in the toolbar and click **Run**. Approve the permission prompt; the script only gets access to this one spreadsheet. This creates the **Responses** and **Campaigns** tabs.
5. **Deploy → New deployment → type: Web app**.
   * Execute as: **Me**
   * Who has access: **Anyone**. Respondents don't sign in, which keeps the survey anonymous.
   * Click **Deploy** and copy the **Web app URL**.
6. Test it: open `<Web app URL>?c=TEST-0001`, complete the survey, and check that a row appears in **Responses**.

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

## Launching a client wave

1. Pick a code such as `ACME-2026Q4`, using letters, digits and dashes.
2. Add a row to the Sheet's **Campaigns** tab: `code = ACME-2026Q4`, `display_name = Acme`, `active = TRUE`.
3. Add `campaigns/ACME-2026Q4.yaml` to the repo, copied from `campaigns/_TEMPLATE.yaml`.
4. Send the link: `<Web app URL>?c=ACME-2026Q4`. The client's sponsor should send it, explaining the purpose and the anonymity rules.
5. When the wave closes, set `active = FALSE`. The link then shows "not active".

## Changing the instrument version

Responses from different instrument versions must not mix. Before deploying a new `Items.gs`, rename the existing **Responses** tab (e.g. `Responses v1.0.0`) and run **setup** again. Item ids that stay the same remain comparable in the benchmark.

## Troubleshooting

| What you see | Cause | Fix |
| --- | --- | --- |
| "Sorry, unable to open the file at this time. Please check the address and try again." | A known Google issue when the browser is signed into **more than one Google account**. It can also mean the URL is malformed, or the deployment was archived. | Open the link in a **private/incognito window**. Respondents are usually signed into one account or none, so they won't see this. Copy the exact link printed by `checkSetup()`. |
| "This survey link is not active" | The link has no `?c=CODE`, the code isn't in the Campaigns tab, or the campaign is set inactive | The page states which one. Run `checkSetup()` and read the execution log. |
| Changes don't appear | The deployment still points to an old version | **Deploy → Manage deployments → pencil → Version: New version → Deploy** |
| Nightly run says secrets are not set | `ARC_SHEET_ID` / `GOOGLE_SERVICE_ACCOUNT` are missing | Step 4 above |
| Nightly run fails with a permission error | The Sheet isn't shared with the service account email | Share the Sheet with it as Viewer |
