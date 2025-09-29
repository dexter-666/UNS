import os
import requests

# Cargar secrets desde GitHub Actions
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg: str):
    """Envía un mensaje de texto al chat de Telegram configurado"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    r = requests.post(url, data=payload)
    if r.status_code == 200:
        print("✅ Mensaje enviado con éxito")
    else:
        print(f"❌ Error al enviar mensaje: {r.text}")

def main():
    send_telegram("🚀 Hola, esta es una PRUEBA desde GitHub Actions")

if __name__ == "__main__":
    main()
