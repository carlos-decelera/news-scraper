import os
import json
import requests
from google import genai

def extract_funding_info(url):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    content = ""
    
    # 1. INTENTO CON JINA READER
    jina_url = f"https://r.jina.ai/{url}"
    headers = {
        "Authorization": f"Bearer {os.getenv('JINA_KEY')}",
        "X-Return-Format": "markdown"
    }
    
    try:
        print(f"--- Intentando extraer con Jina: {url} ---")
        response_jina = requests.get(jina_url, headers=headers, timeout=40) # Aumentado a 40s
        response_jina.raise_for_status()
        content = response_jina.text
    except Exception as e:
        print(f"--- JINA FALLÓ: {e}. Intentando descarga directa... ---")
        # 2. FALLBACK: DESCARGA DIRECTA (Si Jina cae o da timeout)
        try:
            direct_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            direct_res = requests.get(url, headers=direct_headers, timeout=15)
            content = direct_res.text # Obtenemos el HTML crudo (Gemini puede digerirlo)
        except Exception as e_direct:
            print(f"--- ERROR CRÍTICO: No se pudo obtener el contenido de ninguna forma: {e_direct} ---")
            return None

    # Recortar contenido para no exceder tokens innecesariamente
    content = content[:15000] 

    prompt = f"""
    Eres un analista experto en Venture Capital. Tu tarea es extraer información precisa desde el texto proporcionado.
    Si el texto es HTML crudo, ignora las etiquetas y busca la información relevante.

    INSTRUCCIONES:
    1. Analiza si el texto describe una ronda de financiación.
    2. Identifica si la ronda se ha CERRADO o está ABIERTA.
    3. Convierte el monto a número entero (ej: "1.2M" -> 1200000).
    4. Si no hay información clara de una ronda, devuelve un JSON con campos null.

    FORMATO DE SALIDA (JSON):
    {{
        "company_name": "Nombre",
        "amount": 1000000,
        "currency": "EUR",
        "round_type": "Pre-seed/Seed/Serie A/etc",
        "status": "abierta/cerrada"
    }}

    CONTENIDO:
    {content}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"--- ERROR DE GEMINI --- {e}")
        return None