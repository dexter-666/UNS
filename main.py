import os
import requests
from bs4 import BeautifulSoup
import time

# URLs del campus virtual
URL_LOGIN = "https://www.uns.edu.pe/campusvirtual/login/index.php"
URL_CURSO = "https://www.uns.edu.pe/campusvirtual/course/view.php?id=29349"

# Secrets de GitHub
USER = os.getenv("UNS_USER")
PASS = os.getenv("UNS_PASS")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg: str):
    """Envía un mensaje al chat de Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    r = requests.post(url, data=payload)
    if r.status_code != 200:
        print(f"❌ Error al enviar mensaje: {r.text}")

def login():
    """Inicia sesión en el campus virtual y retorna la sesión activa"""
    session = requests.Session()
    r = session.get(URL_LOGIN)
    soup = BeautifulSoup(r.text, "html.parser")
    token = soup.find("input", {"name": "logintoken"})["value"]

    payload = {
        "username": USER,
        "password": PASS,
        "logintoken": token
    }
    r = session.post(URL_LOGIN, data=payload)
    if "loginerrors" in r.text:
        raise Exception("❌ Error: usuario o contraseña incorrectos")
    return session

def get_weeks(session):
    """Obtiene la lista de semanas/secciones del curso"""
    r = session.get(URL_CURSO)
    soup = BeautifulSoup(r.text, "html.parser")
    weeks = [sec.get_text(strip=True) for sec in soup.select(".sectionname")]
    return weeks

def listen_for_commands():
    """Escucha comandos simples de Telegram como /start"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    r = requests.get(url).json()
    if "result" in r:
        for update in r["result"]:
            message = update.get("message", {})
            text = message.get("text", "")
            chat_id = message.get("chat", {}).get("id", "")
            if chat_id and str(chat_id) == CHAT_ID:
                if text.strip().lower() == "/start":
                    send_telegram("✅ Todos los procesos están operativos")

def main():
    try:
        # Login al campus
        session = login()
        send_telegram("🚀 Bot iniciado correctamente\n✅ Login exitoso\n⚡ En espera de cambios o comandos...")

        # Leer semanas actuales
        weeks = get_weeks(session)
        file_cache = "weeks_cache.txt"
        old_weeks = []
        if os.path.exists(file_cache):
            with open(file_cache, "r", encoding="utf-8") as f:
                old_weeks = f.read().splitlines()

        if weeks != old_weeks:
            send_telegram("⚠️ ¡Cambio detectado en el curso!\nSemanas actuales:\n" + "\n".join(weeks))
            with open(file_cache, "w", encoding="utf-8") as f:
                f.write("\n".join(weeks))
        else:
            print("✅ No hay cambios nuevos.")

        # Revisar si hay comandos (como /start)
        listen_for_commands()

    except Exception as e:
        send_telegram(f"❌ Error en el bot: {str(e)}")

if __name__ == "__main__":
    main()
