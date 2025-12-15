# Competitor Monitoring & Contact Scraper

A **Python-based automation pipeline** to monitor competitors using **Google Alerts RSS**, extract relevant news/articles, deduplicate companies, and scrape **official contact information** from competitor websites.

This project is designed for **market intelligence, competitor tracking, and lead research** in domains like **Solar, MNRE, RMS, Remote Monitoring Systems**, etc.

---

## 🔥 What This Project Does 

1. Reads **Google Alerts RSS feeds** (not email)
2. Unwraps Google redirect URLs to real article links
3. Extracts article content + uses RSS titles as fallback
4. Filters articles using your keywords
5. Deduplicates companies using **domain-based logic**
6. Scrapes competitor **/contact pages** for:

   * Email IDs
   * Phone numbers
   * Address hints
7. Exports clean, structured datasets as CSV

No dashboards. No UI. **Pure data pipeline.**

---

## 📁 Project Folder Structure

```
competitor_monitoring/
│
├── config/
│   ├── rss_feeds.yaml          # Google Alerts RSS URLs
│   ├── keywords.yaml           # Keywords to track
│
├── data/
│   └── processed/
│       ├── news.csv            # Filtered news/articles
│       ├── companies.csv       # Deduplicated company list
│       └── contacts.csv        # Scraped contact details
│
├── src/
│   ├── main.py                 # Orchestrator (run this)
│   ├── fetch_rss.py            # RSS reader
│   ├── extract_article.py      # Article text extractor
│   ├── url_utils.py            # Google URL un-wrapper
│   ├── company_resolver.py     # Domain normalization
│   ├── contact_scraper.py      # /contact page scraper
│   └── exporter.py             # CSV writer
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Requirements

* Python **3.9+** recommended

Install dependencies:

```bash
pip install -r requirements.txt
```

**Required libraries**:

* feedparser
* newspaper3k
* beautifulsoup4
* requests
* pyyaml
* pandas
* tldextract
* phonenumbers
* lxml

---

## 🔧 Configuration

### 1️⃣ Google Alerts RSS

Edit:

`config/rss_feeds.yaml`

```yaml
feeds:
  - https://www.google.com/alerts/feeds/XXXXXXXXXXXX
```

> ⚠️ Alert delivery **must be set to RSS**, not email.

---

### 2️⃣ Keywords

Edit:

`config/keywords.yaml`

```yaml
keywords:
  - solar inverter
  - mnre
  - ministry of new and renewable energy
  - rms
  - remote monitoring system
  - datoms
```

Keywords are matched against:

* RSS title
* Extracted article title
* Extracted article body

---

## ▶️ How to Run

From the project root:

```bash
python src/main.py
```

---

## 📤 Output Files

### `news.csv`

Filtered news/articles matching your keywords

| Column           | Description                   |
| ---------------- | ----------------------------- |
| domain           | Source domain                 |
| title            | Article title                 |
| url              | Real article URL              |
| publish_date     | Published date (RSS)          |
| matched_keywords | Keywords that triggered match |

---

### `companies.csv`

Deduplicated company list (domain-based)

| Column     | Description                    |
| ---------- | ------------------------------ |
| domain     | Company domain                 |
| first_seen | First appearance timestamp     |
| last_seen  | Last appearance timestamp      |
| confidence | Data confidence (default: Low) |

---

### `contacts.csv`

Scraped contact details from competitor websites

| Column    | Description              |
| --------- | ------------------------ |
| domain    | Company domain           |
| emails    | Extracted email IDs      |
| phones    | Extracted phone numbers  |
| addresses | Address text (heuristic) |

> ⚠️ Some sites may return empty fields due to JS rendering or obfuscation.

---

## 🧠 Important Design Decisions

* **Domain-based deduplication** → avoids duplicate companies
* **RSS title fallback** → Google Alerts often triggers on title only
* **Google redirect unwrapping** → mandatory for extraction to work
* **Static HTML scraping only** → JS-heavy sites are skipped

This is intentional to keep the system **fast and stable**.

---

## ❌ Known Limitations

* Does NOT handle JS-rendered contact pages (React/Vue)
* Does NOT identify the *actual company mentioned* in articles (publisher ≠ competitor)
* Contact extraction is heuristic, not guaranteed

These are **next-stage upgrades**, not bugs.

---

## 🚀 Recommended Next Upgrades

1. Playwright-based contact scraping (JS-safe)
2. Company entity extraction from article text
3. MNRE website crawler (direct, non-RSS)
4. Confidence scoring (High / Medium / Low)
5. Weekly delta exports + dashboard

---

## 🧪 Debugging Tips

If outputs are empty:

1. Open RSS URL in browser → must contain `<entry>` tags
2. Check console logs for `Skipped (no keyword match)`
3. Verify keywords are not overly strict

The pipeline is **input-sensitive by design**.

---

## 🏁 Final Note

This project gives you:

* **Automation**
* **Repeatability**
* **Structured intelligence**

What you do with the data is up to you.

If you don’t act on it, the problem is not the code.
