# Website Lead Finder

Finds trade businesses (plumbers, electricians, builders, roofers) across Devon
and Cornwall that have **no website listed on Google**, and exports them as a
CSV lead list — good candidates for a "you need a website" pitch.

It works by running a Google Places API (New) Text Search for each
category/town combination (e.g. "plumber in Exeter, UK"), then keeping only
the results where Google has no `websiteUri` on file. An optional second
pass (`verify_leads.py`) re-checks each of those leads with a real web
search, since Places sometimes has no website on file for a business that
does actually have one — it flags possible matches for a quick manual
double-check rather than silently dropping them.

## 1. Set up a Google Places API key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and
   create a new project (or use an existing one).
2. Enable billing on the project. A card is required even to use free credit,
   but new accounts get a free trial credit, and Google also gives an
   ongoing free monthly credit for the Maps Platform — this project's query
   volume (~120 searches) costs a few dollars at Places API Pro-tier pricing,
   comfortably inside that.
3. Enable the **Places API (New)**: APIs & Services → Library → search
   "Places API (New)" → Enable.
4. Create an API key: APIs & Services → Credentials → Create Credentials →
   API key.
5. Restrict the key (recommended): under API restrictions, limit it to
   "Places API (New)" only.

## 2. (Optional) Set up website verification

Skip this if you're happy just trusting the Places `websiteUri` field.
`verify_leads.py` uses the [Brave Search API](https://brave.com/search/api/)
rather than Google — Google restricted "search the entire web" Custom
Search Engines to accounts created before September 2023, so it's no
longer available to new setups. Brave's is simpler anyway:

1. Go to [brave.com/search/api](https://brave.com/search/api/) and sign up.
2. Subscribe to the free "Data for AI" plan (no card-required trial gotchas).
3. Copy the API key from the dashboard — this is your `BRAVE_API_KEY`.

## 3. Install

```bash
pip install -r requirements.txt
cp .env.example .env
# then edit .env: paste your Places API key, and your Brave key if using verification
```

## 4. Run

```bash
python lead_finder.py
```

This searches every town in `config.py` for every category and writes
`leads_devon_cornwall.csv` with columns: name, category searched, town
searched, phone, address, rating, rating count, and a Google Maps link.

Useful flags for a cheaper/faster test run before doing the full sweep:

```bash
python lead_finder.py --towns Exeter Truro --categories plumber --limit 20
```

- `--output PATH` — write the CSV somewhere other than the default.
- `--limit N` — stop after finding N leads.
- `--towns ...` / `--categories ...` — override the town/category lists in
  `config.py` for a single run.

Then, optionally, verify the results:

```bash
python verify_leads.py
```

This re-checks each lead in `leads_devon_cornwall.csv` with a real web
search and adds a `possible_website_found` column — a URL there means a
plausible website turned up for that business, so double-check it manually
before treating the lead as genuinely site-less. An empty value means
either nothing turned up, or the business name was too generic to match
confidently (e.g. mostly common words) — it's a hint, not a guarantee.

## Customizing scope

Edit `TOWNS` and `CATEGORIES` in `config.py` to change geographic coverage or
add/remove trade categories.

## Running it via GitHub Actions instead

If you'd rather not run this locally, there's a workflow that runs the same
script on GitHub's servers and lets you download the CSV afterwards — handy
from a phone/tablet with no terminal.

1. Add your key as a repo secret: repo → **Settings** → **Secrets and
   variables** → **Actions** → **New repository secret** → name it
   `GOOGLE_PLACES_API_KEY`, paste your key as the value.
2. If you want website verification too, add a second repo secret
   `BRAVE_API_KEY` with the key from step 2 above. Without it, the workflow
   still runs — it just skips the verification step.
3. Go to the **Actions** tab → **Run Lead Finder** workflow → **Run
   workflow**. You can optionally fill in `towns` / `categories` / `limit` to
   do a cheap test run first (e.g. towns: `Exeter`, categories: `plumber`,
   limit: `10`) before running the full sweep with everything left blank.
4. Once the run finishes (green check), open it and download the
   `leads-devon-cornwall` artifact from the run summary page — that's your
   CSV, with the `possible_website_found` column included if verification
   ran.

This works the same from the GitHub mobile app as from a browser.
