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
    data = request.get_json()

    video_url = data.get("videoUrl")
    caption = data.get("caption", "")

    if not video_url:
        return jsonify({"error": "Missing videoUrl"}), 400

    try:
        # download video
        response = requests.get(video_url)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            video_path = temp_video.name
            temp_video.write(response.content)

        # login to Instagram
        cl = Client()
        cl.login(IG_USERNAME, IG_PASSWORD)

        # upload reel
        media = cl.clip_upload(video_path, caption)

        os.remove(video_path)

        return jsonify({
            "status": "uploaded",
            "media_id": str(media.pk)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)