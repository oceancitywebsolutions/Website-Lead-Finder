"""Thin wrapper around the Google Places API (New) Text Search endpoint."""

import time

import requests

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# Pro-tier field mask: pulls website + contact/rating info in the search
# response itself, so no separate Place Details call is needed per result.
FIELD_MASK = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.nationalPhoneNumber",
    "places.websiteUri",
    "places.rating",
    "places.userRatingCount",
    "places.googleMapsUri",
])

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2


class PlacesClient:
    def __init__(self, api_key, request_delay_seconds=0.2):
        self.api_key = api_key
        self.request_delay_seconds = request_delay_seconds
        self.session = requests.Session()

    def search_text(self, text_query, page_token=None, included_type=None):
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": FIELD_MASK + ",nextPageToken",
        }
        body = {"textQuery": text_query}
        if included_type:
            body["includedType"] = included_type
        if page_token:
            body["pageToken"] = page_token

        for attempt in range(1, MAX_RETRIES + 1):
            response = self.session.post(SEARCH_URL, headers=headers, json=body)
            if response.status_code == 429 and attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            response.raise_for_status()
            time.sleep(self.request_delay_seconds)
            return response.json()

        response.raise_for_status()

    def search_all_pages(self, text_query, max_pages=3, included_type=None):
        """Yield places across up to `max_pages` pages of results (20 per page)."""
        page_token = None
        for _ in range(max_pages):
            data = self.search_text(text_query, page_token=page_token, included_type=included_type)
            for place in data.get("places", []):
                yield place

            page_token = data.get("nextPageToken")
            if not page_token:
                return
            # Google requires a short delay before a page token becomes valid.
            time.sleep(2)
