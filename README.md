# Website Lead Finder

Finds trade businesses (plumbers, electricians, builders, roofers) across Devon
and Cornwall that have **no website listed on Google**, and exports them as a
CSV lead list — good candidates for a "you need a website" pitch.

It works by running a Google Places API (New) Text Search for each
category/town combination (e.g. "plumber in Exeter, UK"), then keeping only
the results where Google has no `websiteUri` on file.

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

## 2. Install

```bash
pip install -r requirements.txt
cp .env.example .env
# then edit .env and paste your key in place of your-api-key-here
```

## 3. Run

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
2. Go to the **Actions** tab → **Run Lead Finder** workflow → **Run
   workflow**. You can optionally fill in `towns` / `categories` / `limit` to
   do a cheap test run first (e.g. towns: `Exeter`, categories: `plumber`,
   limit: `10`) before running the full sweep with everything left blank.
3. Once the run finishes (green check), open it and download the
   `leads-devon-cornwall` artifact from the run summary page — that's your
   CSV.

This works the same from the GitHub mobile app as from a browser.
