from src.crawler import fetch_relevant_articles
from src.extractor import extract_funding_batch
from src.database import save_funding_data, check_if_url_exists # Asegúrate de tener check_if_url_exists
from src.notifications import send_slack_notification
import time

FEEDS = ["https://elreferente.es/feed/", "https://elreferente.es/feed/?paged=2"]
KEYWORDS = ["funding", "round", "levantar", "ronda", "invest", "busca", "objetivo", "abierta", "raising"]

def main():
    print("--- [INICIO] Ejecutando bot de noticias ---")
    
    # 1. Obtener artículos del RSS
    articles = fetch_relevant_articles(FEEDS, KEYWORDS)
    print(f"--- [INFO] {len(articles)} artículos encontrados en RSS.")

    # 2. Filtrar solo los que NO hemos procesado nunca
    new_articles = []
    for art in articles:
        if not check_if_url_exists(art['url']):
            new_articles.append(art)
    
    if not new_articles:
        print("--- [INFO] Todo al día. Nada nuevo que procesar. ---")
        return

    print(f"--- [IA] Analizando {len(new_articles)} artículos en un solo lote... ---")

    # 3. Llamada única a la IA (Batch)
    # Esto evita el error 429 de cuota agotada
    results = extract_funding_batch(new_articles)

    # 4. Guardar y Notificar
    for info in results:
        # Solo notificamos si la IA encontró una empresa y un monto
        if info.get('company_name') and info.get('amount'):
            print(f"   [OK] Ronda detectada: {info['company_name']} ({info['amount']}€)")
            save_funding_data(info)
            send_slack_notification(info)
        else:
            # Si no era una ronda, lo marcamos como procesado para no volver a leerlo
            # Guardamos un registro vacío o con status "ignorado"
            print(f"   [SKIP] No es una ronda: {info.get('source_url')}")
            save_funding_data({'source_url': info.get('source_url'), 'company_name': None})

    print("--- [FIN] Proceso finalizado correctamente ---")

if __name__ == "__main__":
    main()