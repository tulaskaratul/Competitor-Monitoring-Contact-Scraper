import feedparser

def fetch_articles(rss_urls):
    articles = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", "")
            })
    return articles
