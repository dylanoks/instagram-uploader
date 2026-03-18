

from flask import Flask, request, jsonify
from instagrapi import Client
import requests
import os
import tempfile

app = Flask(__name__)

IG_USERNAME = "imbetterthanyoubuddy"
IG_PASSWORD = "Db102779!"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/upload-reel", methods=["POST"])
def upload_reel():
    data = request.get_json(silent=True) or {}
    video_url = data.get("videoUrl")
    caption = data.get("caption", "")

    if not video_url:
        return jsonify({"error": "Missing videoUrl"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        video_path = temp_video.name

    try:
        response = requests.get(video_url, timeout=120)
        response.raise_for_status()

        with open(video_path, "wb") as f:
            f.write(response.content)

        cl = Client()
        cl.login(IG_USERNAME, IG_PASSWORD)
        media = cl.clip_upload(video_path, caption)

        return jsonify({
            "status": "uploaded",
            "media_id": str(media.pk) if hasattr(media, "pk") else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)