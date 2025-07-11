from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 🔹 Your Telegram Bot Token
TELEGRAM_TOKEN = "8086067009:AAGQ0BXUFW-gc9eGieZCqseIlzu56XwvYnA"
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# 🔹 Home Route (for testing)
@app.route('/')
def home():
    return "✅ Instagram Downloader Bot is Running"

# 🔹 Telegram Webhook Route
@app.route('/bot', methods=['POST'])
def telegram_webhook():
    data = request.get_json()

    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        text = data['message']['text']

        if "instagram.com" in text:
            send_message(chat_id, "📥 Downloading Instagram post...")

            result = download_instagram_post(text)
            if "error" in result:
                send_message(chat_id, f"❌ Error: {result['error']}")
            else:
                for media_url in result['media']:
                    send_media(chat_id, media_url)
                if result.get("caption"):
                    send_message(chat_id, f"📝 Caption: {result['caption'][:100]}")
        else:
            send_message(chat_id, "⚠️ Send a valid Instagram post URL.")

    return "ok", 200

# 🔹 Download function using yabes-desu API
def download_instagram_post(post_url):
    try:
        api_url = f"https://api.yabes-desu.workers.dev/download/instagram/v2?url={post_url}"
        response = requests.get(api_url)
        data = response.json()

        if not data.get("data"):
            return {"error": "Failed to get media from API."}

        result = {
            "caption": data["data"].get("caption", ""),
            "media": [item["url"] for item in data["data"]["medias"]]
        }
        return result

    except Exception as e:
        return {"error": str(e)}

# 🔹 Send message helper
def send_message(chat_id, text):
    requests.post(f"{BASE_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

# 🔹 Send photo/video helper
def send_media(chat_id, media_url):
    if media_url.endswith(".mp4"):
        requests.post(f"{BASE_URL}/sendVideo", json={"chat_id": chat_id, "video": media_url})
    else:
        requests.post(f"{BASE_URL}/sendPhoto", json={"chat_id": chat_id, "photo": media_url})

# 🔹 Start the Flask app (Render will use gunicorn to run this)
if __name__ == '__main__':
    app.run(debug=True)
