import google.generativeai as genai
import requests
import os
import json

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_funding_info(url):
    # 1. Jina Reader extrae el texto limpio de la web
    jina_url = f"https://r.jina.ai/{url}"
    content = requests.get(jina_url).text[:8000]

    # 2. Gemini procesa el texto
    prompt = f"""
    Extrae los datos de esta ronda de financiación en JSON:
    - company_name (nombre de la startup)
    - amount (solo número, sin puntos ni comas, o null si no se dice)
    - currency (ISO: 'USD', 'EUR', etc.)
    - round_type (ej: 'Seed', 'Series A', 'Convertible')

    Texto: {content}
    """
    
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)