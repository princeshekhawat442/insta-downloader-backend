from flask import Flask, request, jsonify
import instaloader
import requests

app = Flask(__name__)
L = instaloader.Instaloader(download_comments=False, save_metadata=False)

# Telegram Bot
BOT_TOKEN = "8086067009:AAGQ0BXUFW-gc9eGieZCqseIlzu56XwvYnA"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

@app.route('/')
def home():
    return "Instagram Downloader + Telegram Bot Running ✅"

@app.route('/download', methods=['GET'])
def download_instagram_post():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        shortcode = url.strip('/').split("/")[-1]
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        media = []
        if post.typename == "GraphSidecar":
            for node in post.get_sidecar_nodes():
                media.append({
                    "url": node.video_url if node.is_video else node.display_url,
                    "type": "video" if node.is_video else "photo"
                })
        else:
            media.append({
                "url": post.video_url if post.is_video else post.url,
                "type": "video" if post.is_video else "photo"
            })

        data = {
            "success": True,
            "media": media,
            "caption": post.caption or "",
            "username": post.owner_username,
            "likes": post.likes,
            "comments": post.comments
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.startswith("/start"):
            reply = "👋 Welcome! Send me any Instagram link to download media."
        elif "instagram.com" in text:
            try:
                res = requests.get(f"{request.url_root}download", params={"url": text})
                post_data = res.json()

                if post_data["success"]:
                    for media in post_data["media"]:
                        send_message(chat_id, media["url"])
                else:
                    send_message(chat_id, f"❌ Error: {post_data.get('error', 'Failed to download.')}")
            except Exception as e:
                send_message(chat_id, f"❌ Exception: {str(e)}")
        else:
            reply = f"🔗 You sent: {text}"
            send_message(chat_id, reply)

    return "OK"

def send_message(chat_id, text):
    payload = {"chat_id": chat_id, "text": text}
    requests.post(TELEGRAM_API_URL, json=payload)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
