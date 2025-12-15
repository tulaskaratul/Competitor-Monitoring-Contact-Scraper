from newspaper import Article

def extract_content(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return {
            "title": article.title,
            "text": article.text,
            "publish_date": str(article.publish_date)
        }
    except Exception:
        return None
