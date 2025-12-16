import re

BLACKLIST = [
    "mnre",
    "ministry of new and renewable energy",
    "government",
    "india",
    "policy",
    "award",
    "scheme"
]

def extract_company_candidates(text):
    """
    Heuristic-based company name extraction.
    Later replace with NER (spaCy).
    """
    candidates = set()

    # Simple pattern: Capitalized word sequences
    pattern = r'\b[A-Z][A-Za-z&.\- ]{2,}\b'
    matches = re.findall(pattern, text)

    for m in matches:
        name = m.strip()
        lname = name.lower()

        if any(b in lname for b in BLACKLIST):
            continue

        if len(name.split()) <= 1:
            continue

        candidates.add(name)

    return list(candidates)
