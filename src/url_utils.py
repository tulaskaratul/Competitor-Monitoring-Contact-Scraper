from urllib.parse import urlparse, parse_qs, unquote

def unwrap_google_url(google_url):
    """
    Extract real URL from Google Alerts redirect link
    """
    parsed = urlparse(google_url)
    qs = parse_qs(parsed.query)

    if "url" in qs:
        return unquote(qs["url"][0])

    return google_url
