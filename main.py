from flask import Flask, request, jsonify
import instaloader
import requests
import time

app = Flask(__name__)

# Telegram Bot Token
TELEGRAM_TOKEN = "8086067009:AAGQ0BXUFW-gc9eGieZCqseIlzu56XwvYnA"
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@app.route('/')
def home():
    return "Bot + Downloader Running"

# ✅ Correct Webhook Route
@app.route(f'/webhook/{TELEGRAM_TOKEN}', methods=['POST'])
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

def download_instagram_post(url):
    try:
        start_time = time.time()
        shortcode = url.strip('/').split('/')[-1]

        L = instaloader.Instaloader(download_comments=False, save_metadata=False)
        L.login('shekhawat_ji_001', 'Prince@0055')  # Use test IG account

        post = instaloader.Post.from_shortcode(L.context, shortcode)

        result = {
            "caption": post.caption,
            "media": [],
            "type": "album" if post.typename == "GraphSidecar" else post.typename
        }

        if post.typename == "GraphSidecar":
            for node in post.get_sidecar_nodes():
                result["media"].append(node.video_url if node.is_video else node.display_url)
        else:
            result["media"].append(post.video_url if post.is_video else post.url)

        result["time_taken"] = round(time.time() - start_time, 2)
        return result

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
