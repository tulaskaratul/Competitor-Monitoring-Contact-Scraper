import tldextract
import re

def extract_domain(url):
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}"

def normalize_company(name):
    name = name.lower()
    name = re.sub(r'(pvt|ltd|private|limited)', '', name)
    return name.strip()
