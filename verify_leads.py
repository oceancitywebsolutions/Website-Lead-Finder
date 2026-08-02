"""Second-pass check on a leads CSV from lead_finder.py.

Google Places sometimes has no `websiteUri` on file for a business that
does actually have a website (the owner just never added it to their
Google Business Profile). This script re-checks each lead with a real web
search and adds a `possible_website_found` column so a human can quickly
confirm or discard borderline leads before pitching them - it's a hint,
not an automatic filter, since name-to-domain matching isn't foolproof.
"""

import argparse
import csv
import os
import re
import sys
import time
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

from config import IGNORED_DOMAINS

SEARCH_URL = "https://www.googleapis.com/customsearch/v1"
RESULTS_PER_QUERY = 5
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2

STOP_WORDS = {
    "ltd", "limited", "services", "service", "the", "and", "co", "company",
    "plumbing", "plumbers", "electrical", "electricians", "building",
    "builders", "roofing", "roofers", "contractors", "solutions",
}


def business_name_tokens(name):
    words = re.findall(r"[a-zA-Z]+", name.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) >= 4]


def domain_of(url):
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def find_possible_website(session, api_key, cse_id, name, town):
    tokens = business_name_tokens(name)
    if not tokens:
        return ""  # nothing distinctive enough in the name to match on

    query = f'"{name}" {town} UK'
    params = {"key": api_key, "cx": cse_id, "q": query, "num": RESULTS_PER_QUERY}

    for attempt in range(1, MAX_RETRIES + 1):
        response = session.get(SEARCH_URL, params=params)
        if response.status_code == 429 and attempt < MAX_RETRIES:
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)
            continue
        response.raise_for_status()
        break

    items = response.json().get("items", [])
    for item in items:
        link = item.get("link", "")
        domain = domain_of(link)
        if not domain or domain in IGNORED_DOMAINS:
            continue
        if any(token in domain for token in tokens):
            return link

    return ""


def verify_rows(rows, api_key, cse_id, delay_seconds):
    session = requests.Session()
    for row in rows:
        print(f"Checking: {row['name']}", file=sys.stderr)
        row["possible_website_found"] = find_possible_website(
            session, api_key, cse_id, row["name"], row["town_searched"]
        )
        time.sleep(delay_seconds)
        yield row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="leads_devon_cornwall.csv", help="Leads CSV from lead_finder.py.")
    parser.add_argument("--output", default=None, help="Where to write the result (defaults to overwriting --input).")
    parser.add_argument("--delay", type=float, default=0.5, help="Seconds to wait between search queries.")
    args = parser.parse_args()
    output_path = args.output or args.input

    load_dotenv()
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    cse_id = os.environ.get("GOOGLE_CSE_ID")
    if not api_key or not cse_id:
        print(
            "Error: GOOGLE_PLACES_API_KEY and GOOGLE_CSE_ID must both be set. "
            "See README for how to create a Programmable Search Engine.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames + ["possible_website_found"]

    verified_rows = list(verify_rows(rows, api_key, cse_id, args.delay))

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(verified_rows)

    flagged = sum(1 for row in verified_rows if row["possible_website_found"])
    print(f"Checked {len(verified_rows)} leads, {flagged} flagged for review. Written to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
