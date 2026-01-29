import os
import requests

def format_amount(amount):
    """Convierte números largos en formato legible (K, M, B)"""
    if not amount or not isinstance(amount, (int, float)):
        return "Undisclosed"
    
    if amount >= 1_000_000_000:
        return f"{amount / 1_000_000_000:.1f}B"
    elif amount >= 1_000_000:
        return f"{amount / 1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"{amount / 1_000:.0f}K"
    return str(amount)

def send_slack_notification(data):
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook:
        print("--- [AVISO] No hay SLACK_WEBHOOK_URL configurado ---")
        return

    # Preparar los datos
    company = data.get('company_name', 'N/A')
    currency_symbol = "€" if data.get('currency') == "EUR" else "$"
    amount_val = format_amount(data.get('amount'))
    round_type = data.get('round_type', 'N/A')
    status = data.get('status', 'N/A')
    url = data.get('source_url', '#')

    # Construir el bloque de texto estilo "tarjeta"
    message_text = (
        f"----------------------------------------\n\n"
        f"*🏢 Company:* {company}\n"
        f"*💰 Amount:* {currency_symbol}{amount_val}\n"
        f"*📊 Round:* {round_type}\n"
        f"*🚥 Status:* {status}\n"
        f"*🔗 URL:* {url}"
    )

    payload = {
        "text": f"Nueva ronda detectada: {company}", # Notificación en el móvil
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message_text
                }
            }
        ]
    }

    try:
        response = requests.post(webhook, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"--- [ERROR SLACK] --- {e}")