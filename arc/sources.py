"""Where responses come from: the private Google Sheet (production) or a CSV (testing, imports).

Respondent-level data is only ever held in memory. Nothing in this module writes it to disk
inside the repository.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

from .instrument import Instrument

RESPONSES_TAB = "Responses"


def from_csv(path: str | Path, inst: Instrument) -> pd.DataFrame:
    p = Path(path)
    files = sorted(p.glob("*.csv")) if p.is_dir() else [p]
    frames = [pd.read_csv(f, dtype=str) for f in files]
    if not frames:
        return pd.DataFrame(columns=inst.columns)
    return pd.concat(frames, ignore_index=True)


def from_google_sheet(inst: Instrument, sheet_id: str | None = None, creds_json: str | None = None) -> pd.DataFrame:
    """Read the Responses tab (and earlier-version Responses tabs) with a Google service account.

    Env vars (set as GitHub Actions secrets):
      ARC_SHEET_ID             - the spreadsheet id from its URL
      GOOGLE_SERVICE_ACCOUNT   - the service-account key JSON (whole file contents)
    The sheet must be shared (Viewer) with the service account's email.
    """
    import gspread  # imported lazily so tests run without Google libraries
    from google.oauth2.service_account import Credentials

    sheet_id = sheet_id or os.environ["ARC_SHEET_ID"]
    info = json.loads(creds_json or os.environ["GOOGLE_SERVICE_ACCOUNT"])
    creds = Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    book = gspread.authorize(creds).open_by_key(sheet_id)
    frames = []
    for ws in book.worksheets():
        if not is_responses_tab(ws.title):
            continue
        values = ws.get_all_values()
        if len(values) < 2:
            continue
        header, rows = values[0], values[1:]
        unknown = set(header) - set(inst.columns) - {"instrument_version"}
        if unknown:
            raise ValueError(f"Tab '{ws.title}' has columns the instrument does not define: {sorted(unknown)}")
        frames.append(pd.DataFrame(rows, columns=header).replace("", pd.NA))
    if not frames:
        return pd.DataFrame(columns=inst.columns)
    return pd.concat(frames, ignore_index=True)


def is_responses_tab(title: str) -> bool:
    """The live Responses tab, plus tabs setup() kept from earlier instrument versions."""
    t = title.strip()
    return t == RESPONSES_TAB or t.startswith(RESPONSES_TAB + " v") or t.startswith(RESPONSES_TAB + " (earlier")
