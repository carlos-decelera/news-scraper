import feedparser

def fetch_relevant_articles(feeds, keywords):
    found = []
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # Filtro básico previo
            if any(k in entry.title.lower() for k in keywords):
                found.append({"title":entry.title, "url": entry.link})
    
    return found