from google import genai
import os
import json
import requests # Faltaba este import

def extract_funding_info(url):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Jina Reader para limpiar el HTML
    jina_url = f"https://r.jina.ai/{url}"
    JINA_KEY = os.getenv("JINA_KEY")
    headers = {
        "Authorization": f"Bearer {JINA_KEY}",
        "X-Return-Format": "markdown",
        "X-Wait-For-Selector": "article",
        "X-With-Generated-Alt": "true"
    }
    try:
        response_jina = requests.get(jina_url, headers=headers, timeout=30)
        content = response_jina.text[:8000]
    except Exception as e:
        print(f"Error al leer con Jina: {e}")
        return None

    # Prompt optimizado
    prompt = f"""
    Eres un analista experto en Venture Capital. Tu tarea es extraer información precisa desde el texto de una noticia.

    INSTRUCCIONES:
    1. Analiza si el texto describe una ronda de financiación.
    2. Identifica si la ronda se ha CERRADO (completada) o está ABIERTA (buscando inversores).
    3. IMPORTANTE: Convierte SIEMPRE el monto a un número entero (ej: "1.5M" -> 1500000, "500k" -> 500000). Si no hay monto, usa null.
    4. Si la moneda es $, convierte mentalmente a € (aprox) o mantén la original pero indícalo en 'currency'.

    FORMATO DE SALIDA (JSON):
    {{
        "company_name": "Nombre de la Startup",
        "amount": 1500000,
        "currency": "EUR",
        "round_type": "Seed, Serie A, etc.",
        "status": "abierta/cerrada"
    }}

    TEXTO A ANALIZAR:
    {content}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"--- ERROR DE GEMINI --- {e}")
        return None