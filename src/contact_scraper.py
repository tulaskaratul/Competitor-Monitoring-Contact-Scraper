import re
import time
import requests
import phonenumbers

from urllib.parse import urljoin
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CompetitorBot/1.0; +https://example.com/bot)"
}

CONTACT_PATHS = [
    "/contact",
    "/contact-us",
    "/contacts",
    "/about",
    "/about-us",
    "/company/contact"
]


def fetch_url(url, timeout=10):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        if resp.status_code == 200:
            return resp.text
    except Exception as e:
        print(f"  ❌ Fetch failed ({url}) —", e)
    return ""


def find_emails(text):
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return list(set(re.findall(pattern, text)))


def find_phones(text, country=None):
    phones = set()
    for match in phonenumbers.PhoneNumberMatcher(text, country):
        phones.add(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))
    return list(phones)


def find_address_candidates(soup):
    """
    Heuristic: texts containing 'address' or postal patterns
    """
    results = []
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines:
        if "address" in line.lower() or re.search(r"\d{5,}", line):
            results.append(line)
    return list(set(results))


def scrape_contact_for_domain(domain):
    """
    Attempt contact scraping for domain with fallbacks
    """
    base = f"https://{domain}"

    found = {
        "domain": domain,
        "emails": [],
        "phones": [],
        "addresses": []
    }

    # try multiple contact paths
    for path in CONTACT_PATHS:
        url = urljoin(base, path)
        print(f"  → Trying {url}")
        html = fetch_url(url)
        if not html:
            continue

        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(separator="\n")

        # extract
        found["emails"].extend(find_emails(text))
        found["phones"].extend(find_phones(text, country="IN"))
        found["addresses"].extend(find_address_candidates(soup))

        # if we got something credible, break
        if found["emails"] or found["phones"] or found["addresses"]:
            break

        # respect polite crawling
        time.sleep(1)

    # dedupe
    found["emails"] = sorted(set(found["emails"]))
    found["phones"] = sorted(set(found["phones"]))
    found["addresses"] = sorted(set(found["addresses"]))

    return found
