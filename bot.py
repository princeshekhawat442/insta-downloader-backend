from flask import Flask, request
import requests

app = Flask(__name__)

# ⚠️ Apna Telegram bot token yahan paste karo
BOT_TOKEN = "8086067009:AAGQ0BXUFW-gc9eGieZCqseIlzu56XwvYnA"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
BACKEND_API_URL = "https://insta-grabber-x.onrender.com/download"

@app.route('/', methods=['GET'])
def home():
    return "Telegram Bot is Running ✅"

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.startswith("/start"):
            reply = "👋 Welcome! Send me any Instagram link to download media."
            send_message(chat_id, reply)

        elif "instagram.com" in text:
            try:
                # Backend API call
                res = requests.get(BACKEND_API_URL, params={"url": text})
                json_data = res.json()

                if json_data.get("success"):
                    for item in json_data["media"]:
                        if item["type"] == "photo":
                            send_photo(chat_id, item["url"])
                        elif item["type"] == "video":
                            send_video(chat_id, item["url"])
                else:
                    send_message(chat_id, "❌ Failed to fetch media: " + json_data.get("error", "Unknown error"))
            except Exception as e:
                send_message(chat_id, f"⚠️ Error: {str(e)}")
        else:
            send_message(chat_id, "🔗 Please send a valid Instagram link.")

    return "OK"

def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

def send_photo(chat_id, photo_url):
    payload = {
        "chat_id": chat_id,
        "photo": photo_url
    }
    requests.post(f"{TELEGRAM_API_URL}/sendPhoto", json=payload)

def send_video(chat_id, video_url):
    payload = {
        "chat_id": chat_id,
        "video": video_url
    }
    requests.post(f"{TELEGRAM_API_URL}/sendVideo", json=payload)

if __name__ == '__main__':
    app.run()
