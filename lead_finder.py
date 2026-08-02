"""Find trade businesses in Devon & Cornwall with no listed website and
export them to a CSV lead list.
"""

import argparse
import csv
import os
import sys

from dotenv import load_dotenv

from config import CATEGORIES, CATEGORY_TYPES, TOWNS
from places_client import PlacesClient

DEFAULT_OUTPUT_PATH = "leads_devon_cornwall.csv"

CSV_FIELDS = [
    "name",
    "category_searched",
    "town_searched",
    "phone",
    "address",
    "rating",
    "rating_count",
    "maps_url",
]


def place_to_row(place, category, town):
    return {
        "name": place.get("displayName", {}).get("text", ""),
        "category_searched": category,
        "town_searched": town,
        "phone": place.get("nationalPhoneNumber", ""),
        "address": place.get("formattedAddress", ""),
        "rating": place.get("rating", ""),
        "rating_count": place.get("userRatingCount", ""),
        "maps_url": place.get("googleMapsUri", ""),
    }


def find_leads(client, towns, categories, limit=None):
    """Search every category/town combination and yield leads (places with
    no websiteUri), deduped by place id."""
    seen_place_ids = set()
    leads_found = 0

    for town in towns:
        for category in categories:
            query = f"{category} in {town}, UK"
            included_type = CATEGORY_TYPES.get(category)
            print(f"Searching: {query}", file=sys.stderr)

            for place in client.search_all_pages(query, included_type=included_type):
                place_id = place.get("id")
                if not place_id or place_id in seen_place_ids:
                    continue
                seen_place_ids.add(place_id)

                if place.get("websiteUri"):
                    continue  # has a website already, not a lead

                leads_found += 1
                yield place_to_row(place, category, town)

                if limit and leads_found >= limit:
                    return


def write_csv(rows, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", default=DEFAULT_OUTPUT_PATH, help="Path to write the leads CSV to."
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Stop after finding this many leads (useful for testing)."
    )
    parser.add_argument(
        "--towns", nargs="+", default=None, help="Override the town list (for a quick test run)."
    )
    parser.add_argument(
        "--categories", nargs="+", default=None, help="Override the category list (for a quick test run)."
    )
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print(
            "Error: GOOGLE_PLACES_API_KEY is not set. Copy .env.example to .env "
            "and add your key.",
            file=sys.stderr,
        )
        sys.exit(1)

    client = PlacesClient(api_key)
    towns = args.towns or TOWNS
    categories = args.categories or CATEGORIES

    rows = list(find_leads(client, towns, categories, limit=args.limit))
    write_csv(rows, args.output)
    print(f"Found {len(rows)} leads. Written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
