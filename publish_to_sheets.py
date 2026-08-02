"""Publish a leads CSV to a new tab in a Google Sheet, via a service account.

Never touches any existing tab - each run creates its own new, timestamped
tab, so a hand-maintained tracking tab in the same spreadsheet is never at
risk of being overwritten. Results are meant to be reviewed and copied
across manually from there.
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def load_rows(input_path):
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    return fieldnames, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="leads_devon_cornwall.csv", help="Leads CSV to publish.")
    parser.add_argument("--tab-name", default=None, help="Override the new tab's name (default: 'Import <timestamp>').")
    args = parser.parse_args()

    load_dotenv()
    creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not creds_json or not sheet_id:
        print(
            "Error: GOOGLE_SERVICE_ACCOUNT_JSON and GOOGLE_SHEET_ID must both be "
            "set. See README for how to set up the service account.",
            file=sys.stderr,
        )
        sys.exit(1)

    fieldnames, rows = load_rows(args.input)
    if not rows:
        print("No leads to publish - nothing written.", file=sys.stderr)
        return

    credentials = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(sheet_id)

    tab_name = args.tab_name or f"Import {datetime.now(timezone.utc):%Y-%m-%d %H-%M-%S}"
    worksheet = spreadsheet.add_worksheet(title=tab_name, rows=len(rows) + 1, cols=max(len(fieldnames), 1))

    values = [fieldnames] + [[row.get(field, "") for field in fieldnames] for row in rows]
    worksheet.update(values)

    print(f"Published {len(rows)} leads to new tab '{tab_name}'.", file=sys.stderr)


if __name__ == "__main__":
    main()
