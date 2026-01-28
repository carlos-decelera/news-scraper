from src.crawler import fetch_relevant_articles
from src.extractor import extract_funding_info
from src.database import save_funding_data
from src.notifications import send_slack_notification

FEEDS = ["https://techcrunch.com/feed/", "https://elreferente.es/feed/"]
KEYWORDS = ["funding", "round", "levantar", "ronda", "invest"]

def main():
    articles = fetch_relevant_articles(FEEDS, KEYWORDS)
    for art in articles:
        # Primero intentamos guardar la URL vacía para chequear si es nueva
        temp_data = {'company_name': 'N/A', 'source_url': art['url']}
        if save_funding_data(temp_data):
            # Si es nueva (no existía), procesamos con IA
            info = extract_funding_info(art['url'])
            info['source_url'] = art['url']
            save_funding_data(info) # Actualizamos con la info real
            send_slack_notification(info)

if __name__ == "__main__":
    main()