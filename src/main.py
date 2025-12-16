import yaml
import re
import time
import requests
import feedparser
import tldextract
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote, urljoin
from bs4 import BeautifulSoup
import pandas as pd
import phonenumbers


# ==============================
# CONFIG
# ==============================
def load_yaml(path, key):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f).get(key, [])


RSS_FEEDS = load_yaml("config/rss_feeds.yaml", "feeds")
KEYWORDS = [k.lower() for k in load_yaml("config/keywords.yaml", "keywords")]
PUBLISHERS = set(load_yaml("config/publishers.yaml", "publishers"))


# ==============================
# UTILITIES
# ==============================
def unwrap_google_url(url):
    qs = parse_qs(urlparse(url).query)
    return unquote(qs["url"][0]) if "url" in qs else url


def extract_domain(url):
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}"


# ==============================
# ARTICLE EXTRACTION
# ==============================
def extract_article(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")
        title = soup.title.text.strip() if soup.title else ""
        text = " ".join(p.get_text(" ", strip=True) for p in soup.find_all("p"))
        return title, text
    except Exception:
        return "", ""


# ==============================
# ENTITY EXTRACTION (STRICT)
# ==============================
BLACKLIST_TERMS = {
    "ministry", "government", "india", "policy",
    "scheme", "award", "department", "authority"
}


def extract_companies(text):
    """
    Returns ONLY potential operating companies.
    If empty → article is ignored.
    """
    candidates = set()
    pattern = r"\b[A-Z][A-Za-z&.\- ]{2,}\b"

    for match in re.findall(pattern, text):
        name = match.strip()
        lname = name.lower()

        if len(name.split()) < 2:
            continue
        if any(b in lname for b in BLACKLIST_TERMS):
            continue
        if any(pub in lname for pub in PUBLISHERS):
            continue

        candidates.add(name)

    return list(candidates)


# ==============================
# WEBSITE RESOLUTION
# ==============================
def resolve_website(company):
    try:
        q = f"https://www.google.com/search?q={company}+official+website"
        r = requests.get(q, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")

        for a in soup.select("a"):
            href = a.get("href", "")
            if href.startswith("http") and "google" not in href:
                return href
    except Exception:
        pass

    return None


# ==============================
# CONTACT SCRAPER
# ==============================
CONTACT_PATHS = ["/contact", "/contact-us", "/about", "/about-us"]

def scrape_contact(domain):
    base = f"https://{domain}"
    emails, phones, addresses = set(), set(), set()

    for path in CONTACT_PATHS:
        try:
            r = requests.get(urljoin(base, path), timeout=10,
                             headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "lxml")
            text = soup.get_text("\n")

            emails.update(re.findall(
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))

            for m in phonenumbers.PhoneNumberMatcher(text, "IN"):
                phones.add(phonenumbers.format_number(
                    m.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))

            for line in text.split("\n"):
                if "address" in line.lower():
                    addresses.add(line.strip())

            if emails or phones:
                break

            time.sleep(1)

        except Exception:
            continue

    return {
        "emails": "; ".join(sorted(emails)),
        "phones": "; ".join(sorted(phones)),
        "addresses": "; ".join(sorted(addresses))
    }


# ==============================
# PIPELINE
# ==============================
companies = {}
news_rows = []

for feed in RSS_FEEDS:
    entries = feedparser.parse(feed).entries

    for item in entries:
        real_url = unwrap_google_url(item.link)
        title, text = extract_article(real_url)
        combined = f"{item.title.lower()} {title.lower()} {text.lower()}"

        if not any(k in combined for k in KEYWORDS):
            continue

        extracted_companies = extract_companies(text)

        # 🔴 HARD STOP: no companies → ignore article
        if not extracted_companies:
            continue

        news_rows.append({
            "article": real_url,
            "title": item.title,
            "published": item.get("published", "")
        })

        for company in extracted_companies:
            website = resolve_website(company)
            if not website:
                continue

            domain = extract_domain(website)

            # 🔴 FINAL SAFETY CHECK
            if domain in PUBLISHERS:
                continue

            now = datetime.utcnow().isoformat()

            companies.setdefault(domain, {
                "company_name": company,
                "domain": domain,
                "website": website,
                "first_seen": now,
                "last_seen": now,
                "confidence": "Medium"
            })


# ==============================
# CONTACT SCRAPING
# ==============================
contacts = []
for domain, c in companies.items():
    print("Contact scrape →", domain)
    contact = scrape_contact(domain)

    contacts.append({
        "company_name": c["company_name"],
        "domain": domain,
        "website": c["website"],
        **contact
    })


# ==============================
# EXPORT
# ==============================
pd.DataFrame(news_rows).to_csv("data/processed/news.csv", index=False)
pd.DataFrame(companies.values()).to_csv("data/processed/companies.csv", index=False)
pd.DataFrame(contacts).to_csv("data/processed/contacts.csv", index=False)

print("✅ Clean competitor-only data generated")
print("🎯 No publishers included")
