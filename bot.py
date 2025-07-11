from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = "8086067009:AAGQ0BXUFW-gc9eGieZCqseIlzu56XwvYnA"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

@app.route('/', methods=['GET'])
def home():
    return "Telegram Bot is Running ✅"

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # Basic reply
        if text.startswith("/start"):
            reply = "👋 Welcome! Send me any Instagram link to download media."
        else:
            reply = f"🔗 You sent: {text}"

        send_message(chat_id, reply)

    return "OK"

def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(TELEGRAM_API_URL, json=payload)

if __name__ == '__main__':
    app.run()
