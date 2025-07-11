from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "8086067009:AAGQ0BXUFW-gc9eGieZCqseIlzu56XwvYnA"
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@app.route('/')
def home():
    return "Bot + Downloader Running"

@app.route('/bot', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        text = data['message']['text']

        if "instagram.com" in text:
            send_message(chat_id, "📥 Downloading Instagram post...")

            result = download_from_saveig(text)
            if result.get("error"):
                send_message(chat_id, f"❌ Error: {result['error']}")
            else:
                for media in result["media"]:
                    send_media(chat_id, media)
                if result.get("caption"):
                    send_message(chat_id, f"📝 Caption: {result['caption'][:100]}")
        else:
            send_message(chat_id, "⚠️ Send a valid Instagram post URL.")

    return "ok", 200

def download_from_saveig(insta_url):
    try:
        api = "https://saveig.app/api/ajaxSearch"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0",
        }
        data = f"q={insta_url}&t=media"
        res = requests.post(api, data=data, headers=headers)
        json_data = res.json()

        media_links = []
        for item in json_data.get("medias", []):
            media_links.append(item.get("url"))

        return {
            "caption": json_data.get("title"),
            "media": media_links
        }
    except Exception as e:
        return {"error": str(e)}

def send_message(chat_id, text):
    requests.post(f"{BASE_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

def send_media(chat_id, media_url):
    if media_url.endswith(".mp4"):
        requests.post(f"{BASE_URL}/sendVideo", json={"chat_id": chat_id, "video": media_url})
    else:
        requests.post(f"{BASE_URL}/sendPhoto", json={"chat_id": chat_id, "photo": media_url})

if __name__ == '__main__':
    app.run(debug=True)
