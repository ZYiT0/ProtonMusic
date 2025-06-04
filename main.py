from flask import Flask, render_template, request, send_file, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

def get_video_info(url):
    with YoutubeDL({'quiet': True}) as ydl:
        return ydl.extract_info(url, download=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    data = request.form
    url = data.get("url")
    quality = data.get("quality", "720")
    format_choice = data.get("format", "mp4").lower()

    try:
        info = get_video_info(url)
        title = info.get('title', 'video').replace('/', '_').replace('\\', '_')

        if format_choice == 'mp3':
            filename = f"{title}.mp3"
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': filename,
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        elif format_choice == 'webm':
            filename = f"{title}.webm"
            ydl_opts = {
                'format': 'bestaudio[ext=webm]',
                'outtmpl': filename,
                'quiet': True,
            }
        else:  # mp4
            filename = f"{title}.mp4"
            ydl_opts = {
                'format': f'bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=m4a]/best[ext=mp4][height<={quality}]',
                'outtmpl': filename,
                'quiet': True,
                'merge_output_format': 'mp4',
            }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
