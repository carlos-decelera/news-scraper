import os
import requests

def send_slack_notification(data):
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook: return

    # Icono dinámico según el estado
    status_icon = "🟢 [CERRADA]" if data.get('status') == "cerrada" else "🔍 [ABIERTA/BUSCANDO]"
    
    payload = {
        "blocks": [
            {
                "type": "header", 
                "text": {"type": "plain_text", "text": f"{status_icon} Nueva Oportunidad"}
            },
            {
                "type": "section", 
                "text": {
                    "type": "mrkdwn", 
                    "text": f"*Empresa:* {data['company_name']}\n*Monto:* {data['amount']} {data['currency']}\n*Tipo:* {data['round_type']}\n*Estado:* {data.get('status', 'N/A')}"
                }
            },
            {
                "type": "section", 
                "text": {"type": "mrkdwn", "text": f"<{data['source_url']}|Ver noticia original>"}
            }
        ]
    }
    requests.post(webhook, json=payload)