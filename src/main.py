import yaml
from datetime import datetime

from fetch_rss import fetch_articles
from extract_article import extract_content
from company_resolver import extract_domain
from exporter import export_csv
from url_utils import unwrap_google_url
from contact_scraper import scrape_contact_for_domain


def load_yaml(path, key):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get(key, [])


# --------------------
# Load config
# --------------------
rss_urls = load_yaml("config/rss_feeds.yaml", "feeds")
keywords = [k.lower() for k in load_yaml("config/keywords.yaml", "keywords")]

print("RSS URLs loaded:", len(rss_urls))
print("Keywords loaded:", keywords)

# --------------------
# Fetch RSS items
# --------------------
articles = fetch_articles(rss_urls)
print("Total RSS items:", len(articles))

if not articles:
    print("❌ No items found in RSS feeds.")
    exit(0)

news_rows = []
companies = {}

# --------------------
# Process articles
# --------------------
for item in articles:
    raw_url = item["link"]
    real_url = unwrap_google_url(raw_url)

    print("\nProcessing:", real_url)

    content = extract_content(real_url)

    rss_title = (item.get("title") or "").lower()
    extracted_title = (content.get("title") or "").lower() if content else ""
    extracted_text = (content.get("text") or "").lower() if content else ""

    combined_text = " ".join([rss_title, extracted_title, extracted_text])

    if not any(k in combined_text for k in keywords):
        print("⏭️ Skipped (no keyword match)")
        continue

    domain = extract_domain(real_url)
    now = datetime.utcnow().isoformat()

    # ---- news table ----
    news_rows.append({
        "domain": domain,
        "title": item.get("title"),
        "url": real_url,
        "publish_date": item.get("published"),
        "matched_keywords": ", ".join([k for k in keywords if k in combined_text])
    })

    # ---- company table ----
    if domain not in companies:
        companies[domain] = {
            "domain": domain,
            "first_seen": now,
            "last_seen": now,
            "confidence": "Low"
        }
    else:
        companies[domain]["last_seen"] = now


# --------------------
# Export NEWS + COMPANIES
# --------------------
if news_rows:
    export_csv(news_rows, "data/processed/news.csv")
    print(f"\n✅ news.csv written ({len(news_rows)} rows)")
else:
    print("\n⚠️ news.csv NOT written")

if companies:
    export_csv(list(companies.values()), "data/processed/companies.csv")
    print(f"✅ companies.csv written ({len(companies)} rows)")
else:
    print("⚠️ companies.csv NOT written")


# --------------------
# Scrape CONTACT pages
# --------------------
print("\n🔍 Scraping contact pages...\n")

contacts_rows = []

for domain in companies.keys():
    print(f"Contact scrape → {domain}")
    result = scrape_contact_for_domain(domain)

    contacts_rows.append({
        "domain": domain,
        "emails": "; ".join(result["emails"]),
        "phones": "; ".join(result["phones"]),
        "addresses": "; ".join(result["addresses"])
    })

# --------------------
# Export CONTACTS
# --------------------
if contacts_rows:
    export_csv(contacts_rows, "data/processed/contacts.csv")
    print(f"\n✅ contacts.csv written ({len(contacts_rows)} rows)")
else:
    print("\n⚠️ contacts.csv NOT written")

print("\n🎯 Run complete")
