def dedupe_by_domain(companies):
    unique = {}
    for c in companies:
        domain = c["domain"]
        if domain not in unique:
            unique[domain] = c
        else:
            unique[domain]["last_seen"] = c["last_seen"]
    return list(unique.values())
