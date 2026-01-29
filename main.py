from src.crawler import fetch_relevant_articles
from src.extractor import extract_funding_info
from src.database import save_funding_data
from src.notifications import send_slack_notification
import time

FEEDS = ["https://elreferente.es/feed/", "https://elreferente.es/feed/?paged=2"]
KEYWORDS = ["funding", "round", "levantar", "ronda", "invest", "busca", "objetivo", "abierta", "raising"]

def main():
    print("--- [INICIO] Ejecutando bot de noticias ---")
    articles = fetch_relevant_articles(FEEDS, KEYWORDS)
    print(f"--- [INFO] Se han encontrado {len(articles)} artículos en los RSS.")

    for art in articles:
        print(f"--- [PROCESANDO] URL: {art['url']}")
        temp_data = {'company_name': 'N/A', 'source_url': art['url']}
        
        # Si save_funding_data devuelve False, es que la URL ya existe en la BD
        if save_funding_data(temp_data):
            time.sleep(10)
            print(f"    [NUEVO] El artículo no estaba en la BD. Analizando con IA...")
            info = extract_funding_info(art['url'])
            
            if info:
                print(f"    [IA OK] Datos extraídos: {info['company_name']} - {info['amount']}")
                info['source_url'] = art['url']
                save_funding_data(info)
                
                print(f"    [SLACK] Enviando notificación...")
                send_slack_notification(info)
            else:
                print(f"    [IA ERROR] No se pudo extraer información del artículo.")
        else:
            print(f"    [OMITIDO] El artículo ya existe en la base de datos.")

    print("--- [FIN] Proceso finalizado ---")

if __name__ == "__main__":
    main()