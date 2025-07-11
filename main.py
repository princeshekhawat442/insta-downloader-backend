from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 🔹 Telegram Bot Token
TELEGRAM_TOKEN = "8086067009:AAGQ0BXUFW-gc9eGieZCqseIlzu56XwvYnA"
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@app.route('/')
def home():
    return "Bot + Downloader Running"

# 🔹 Telegram Webhook
@app.route('/bot', methods=['POST'])
def telegram_webhook():
    data = request.get_json()

    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        text = data['message']['text']

        if "instagram.com" in text:
            send_message(chat_id, "📥 Downloading Instagram post...")

            try:
                response = download_instagram_post(text)
                if "error" in response:
                    send_message(chat_id, f"❌ Error: {response['error']}")
                else:
                    for media_url in response["media"]:
                        send_media(chat_id, media_url)
                    if response["caption"]:
                        send_message(chat_id, f"📝 Caption: {response['caption'][:100]}")
            except Exception as e:
                send_message(chat_id, f"⚠️ Failed: {str(e)}")
        else:
            send_message(chat_id, "⚠️ Send a valid Instagram post URL.")

    return "ok", 200

# 🔹 Instagram Download via Free API
def download_instagram_post(insta_url):
    try:
        api_url = f"https://api.yabes-desu.workers.dev/download/instagram/v2?url={insta_url}"
        res = requests.get(api_url)

        if res.status_code != 200:
            return {"error": "API Error. Please try again."}

        data = res.json()
        result = {
            "caption": data.get("caption", ""),
            "media": [m["url"] for m in data.get("media", [])],
            "type": data.get("type", "unknown")
        }
        return result

    except Exception as e:
        return {"error": str(e)}

# 🔹 Telegram Send Helpers
def send_message(chat_id, text):
    requests.post(f"{BASE_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

def send_media(chat_id, media_url):
    if media_url.endswith(".mp4"):
        requests.post(f"{BASE_URL}/sendVideo", json={"chat_id": chat_id, "video": media_url})
    else:
        requests.post(f"{BASE_URL}/sendPhoto", json={"chat_id": chat_id, "photo": media_url})

if __name__ == '__main__':
    app.run(debug=True)
