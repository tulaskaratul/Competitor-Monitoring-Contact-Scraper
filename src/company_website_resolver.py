import requests
from bs4 import BeautifulSoup

def resolve_company_website(company_name):
    query = f"https://www.google.com/search?q={company_name}+official+website"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(query, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "lxml")

    for a in soup.select("a"):
        href = a.get("href", "")
        if href.startswith("http") and "google" not in href:
            return href

    return None
