from google import genai
import os
import json
import requests # Faltaba este import

def extract_funding_info(url):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Jina Reader para limpiar el HTML
    jina_url = f"https://r.jina.ai/{url}"
    try:
        response_jina = requests.get(jina_url, timeout=10)
        content = response_jina.text[:12000] # Un poco más de margen
    except Exception as e:
        print(f"Error al leer con Jina: {e}")
        return None

    # Prompt optimizado
    prompt = f"""
    Eres un analista experto en Venture Capital. Tu tarea es extraer información precisa sobre rondas de financiación desde el texto de una noticia.

    INSTRUCCIONES:
    1. Identifica si la noticia habla de una ronda que se ha CERRADO (completada) o que se ha ABIERTO (la empresa está buscando inversores).
    2. El nombre de la empresa debe ser el nombre propio, no descripciones.
    3. Si el monto no es exacto, usa el número más cercano (ej: "más de 1M" -> 1000000).
    4. El campo 'status' debe ser estrictamente "abierta" o "cerrada".

    FORMATO DE SALIDA (JSON):
    {{
        "company_name": "Nombre",
        "amount": 123456,
        "currency": "EUR/USD",
        "round_type": "Seed, Serie A, Bridge, etc.",
        "status": "abierta/cerrada"
    }}

    TEXTO A ANALIZAR:
    {content}
    """
    
    try:
        response = client.models.generate_content(
            model="models/gemini-3-flash-preview",
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"--- ERROR DE GEMINI --- {e}")
        return None