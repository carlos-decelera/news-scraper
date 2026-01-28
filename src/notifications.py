import requests
import os

def send_slack_notification(data):
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook: return

    payload = {
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": "💰 ¡Nueva Ronda Detectada!"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Empresa:* {data['company_name']}\n*Monto:* {data['amount']} {data['currency']}\n*Tipo:* {data['round_type']}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"<{data['source_url']}|Ver noticia original>"}}
        ]
    }
    requests.post(webhook, json=payload)