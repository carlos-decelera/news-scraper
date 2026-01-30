import os
import json
import requests
import re
from google import genai

def clean_html_light(html_text):
    """Limpia el HTML para que Gemini no se pierda en el código."""
    clean = re.sub(r'<(script|style).*?>.*?</\1>', '', html_text, flags=re.DOTALL)
    clean = re.sub(r'<.*?>', ' ', clean)
    return ' '.join(clean.split())[:5000]

def get_article_content(url):
    """
    Estrategia de dos capas:
    1. Intenta Jina Reader (formato limpio).
    2. Si da timeout o error, descarga el HTML directo.
    """
    jina_url = f"https://r.jina.ai/{url}"
    headers = {
        "Authorization": f"Bearer {os.getenv('JINA_KEY')}",
        "X-Return-Format": "markdown"
    }
    
    try:
        print(f"      [Lector] Intentando Jina: {url[:50]}...")
        res = requests.get(jina_url, headers=headers, timeout=25)
        res.raise_for_status()
        return res.text
    except Exception as e:
        print(f"      [!] Jina falló o tardó mucho. Usando descarga directa.")
        try:
            headers_direct = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
            res = requests.get(url, headers=headers_direct, timeout=15)
            return clean_html_light(res.text)
        except Exception as e_final:
            return f"Error al obtener contenido: {str(e_final)}"

def extract_funding_batch(articles_list):
    """
    Recibe una lista de artículos y los procesa en UNA SOLA llamada a Gemini.
    Ahorra cuota (Error 429) y es más rápido.
    """
    if not articles_list:
        return []

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Preparamos el contexto con todos los artículos juntos
    batch_context = ""
    for i, art in enumerate(articles_list):
        content = get_article_content(art['url'])
        batch_context += f"\n--- ARTÍCULO {i+1} ---\n"
        batch_context += f"URL: {art['url']}\n"
        batch_context += f"CONTENIDO: {content}\n"

    prompt = f"""
    Eres un analista de inversiones. Analiza estas {len(articles_list)} noticias y extrae datos de rondas de financiación.
    
    REGLAS:
    1. Extrae: 'company_name', 'amount' (entero, ej: 1500000), 'currency', 'round_type' y 'status' (abierta/cerrada).
    2. Mantén cada 'source_url' unida a sus datos correctos. No mezcles noticias.
    3. Si una noticia NO es una ronda de inversión, pon los campos a null.
    4. Devuelve SIEMPRE un Array de JSON.

    NOTICIAS:
    {batch_context}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"   [ERROR GEMINI] {e}")
        return []