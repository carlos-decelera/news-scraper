from google import genai # Nueva librería oficial
import os
import json

def extract_funding_info(url):
    # Usamos la nueva SDK 'google-genai'
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    jina_url = f"https://r.jina.ai/{url}"
    content = requests.get(jina_url).text[:8000]

    prompt = f"Extrae los datos de esta ronda en JSON: company_name, amount, currency, round_type. Texto: {content}"
    
    # La sintaxis ahora es más limpia
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
        }
    )
    return json.loads(response.text)