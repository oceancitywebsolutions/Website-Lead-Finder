"""Search configuration: towns to cover and trade categories to search for."""

# Devon & Cornwall towns, used to build "<category> in <town>, UK" queries.
# Text Search returns at most 20 results per page (60 with pagination), so
# searching per-town keeps each query's result set well under that cap.
TOWNS = [
    # Devon
    "Exeter", "Plymouth", "Torquay", "Paignton", "Newton Abbot",
    "Barnstaple", "Exmouth", "Tiverton", "Bideford", "Okehampton",
    "Totnes", "Dartmouth", "Kingsbridge", "Honiton", "Sidmouth",
    "Axminster", "Crediton", "Ilfracombe", "Tavistock", "South Molton",
    # Cornwall
    "Truro", "Falmouth", "Penzance", "St Austell", "Newquay",
    "Bodmin", "Camborne", "Redruth", "Launceston", "Liskeard",
    "Saltash", "Helston", "St Ives", "Wadebridge", "Bude",
]

CATEGORIES = [
    "plumber",
    "electrician",
    "builder",
    "roofer",
]

# Domains that are directories/social platforms, not a business's own site.
# A match against one of these in verify_leads.py is ignored rather than
# treated as evidence the business already has a website.
IGNORED_DOMAINS = {
    "facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com",
    "yell.com", "thomsonlocal.com", "checkatrade.com", "trustpilot.com",
    "tripadvisor.com", "tripadvisor.co.uk", "foursquare.com", "yelp.com",
    "google.com", "maps.google.com", "goo.gl", "freeindex.co.uk",
    "cylex-uk.co.uk", "scoot.co.uk", "192.com", "bing.com", "youtube.com",
    "companieshouse.gov.uk", "gov.uk", "wikipedia.org", "indeed.com",
    "ratedpeople.com", "rated-people.com", "mybuilder.com", "bark.com",
    "houzz.co.uk", "houzz.com", "gumtree.com", "nextdoor.co.uk",
}
