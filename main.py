from src.crawler import fetch_relevant_articles
from src.extractor import extract_funding_info
from src.database import save_funding_data, SessionLocal, Company # Importamos SessionLocal y el modelo
from src.notifications import send_slack_notification

FEEDS = ["https://techcrunch.com/feed/", "https://elreferente.es/feed/"]
# He añadido más keywords para que no se pierda nada por el camino
KEYWORDS = ["funding", "round", "levantar", "ronda", "invest", "inversión", "seed", "serie", "capital"]

def main():
    print("--- [INICIO] Ejecutando bot de noticias ---")
    articles = fetch_relevant_articles(FEEDS, KEYWORDS)
    print(f"--- [INFO] Se han encontrado {len(articles)} artículos potenciales en los RSS.")

    # Abrimos la sesión de DB una sola vez para ser eficientes
    db = SessionLocal()
    
    try:
        for art in articles:
            print(f"--- [REVISANDO] URL: {art['url']}")
            
            # 1. COMPROBACIÓN: ¿Ya existe esta URL en nuestra tabla de Company?
            # Usamos 'reference' que es donde guardamos la URL
            exists = db.query(Company).filter(Company.reference == art['url']).first()
            
            if not exists:
                print(f"    [NUEVO] No está en la BD. Analizando con IA...")
                
                # 2. IA: Solo llamamos a la IA si el artículo es realmente nuevo
                info = extract_funding_info(art['url'])
                
                if info and info.get('company_name'):
                    print(f"    [IA OK] Datos: {info['company_name']} - {info.get('amount', 'N/A')}")
                    info['source_url'] = art['url']
                    
                    # 3. GUARDAR: Ahora guardamos la información real completa
                    if save_funding_data(info):
                        print(f"    [DB] Guardado con éxito.")
                        
                        # 4. NOTIFICAR: Solo enviamos Slack si se guardó correctamente
                        print(f"    [SLACK] Enviando notificación...")
                        send_slack_notification(info)
                else:
                    print(f"    [IA ERROR] La IA no pudo extraer datos válidos.")
            else:
                print(f"    [OMITIDO] Esta noticia ya fue procesada anteriormente.")

    except Exception as e:
        print(f"--- [ERROR CRÍTICO] {e} ---")
    finally:
        db.close() # Cerramos la sesión siempre
        print("--- [FIN] Proceso finalizado ---")

if __name__ == "__main__":
    main()