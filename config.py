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
