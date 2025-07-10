from flask import Flask, request, jsonify
import instaloader
import os

app = Flask(__name__)
L = instaloader.Instaloader(download_comments=False, save_metadata=False)

@app.route("/")
def root():
    return "✅ Insta Downloader Backend is running"

@app.route("/download", methods=["GET"])
def download():
    url = request.args.get("url")
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

        return jsonify({
            "success": True,
            "media": media,
            "caption": post.caption or "",
            "username": post.owner_username,
            "likes": post.likes,
            "comments": post.comments
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

