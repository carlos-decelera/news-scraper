from google import genai
import os
import json
import requests # Faltaba este import

def extract_funding_info(url):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Jina Reader para limpiar el HTML y convertirlo a Markdown
    jina_url = f"https://r.jina.ai/{url}"
    try:
        response_jina = requests.get(jina_url, timeout=10)
        content = response_jina.text[:10000] # Un poco más de contexto
    except Exception as e:
        print(f"Error al leer con Jina: {e}")
        return None

    prompt = (
        "Eres un analista financiero. Extrae los datos de la ronda de inversión "
        "en el siguiente JSON: {\"company_name\": string, \"amount\": number, \"currency\": string, \"round_type\": string}. "
        f"Texto: {content}"
    )
    
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config={'response_mime_type': 'application/json'}
    )
    
    return json.loads(response.text)