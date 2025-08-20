import webview
import threading
import os
import sys
import subprocess
import time
from flask import Flask, request, jsonify
import yt_dlp

# Flask Server für die Backend-Funktionen
app = Flask(__name__)

# Pfade
base_dir = os.path.dirname(os.path.abspath(__file__))
download_path_video = os.path.join(base_dir, 'Downloads', 'Videos')
download_path_music = os.path.join(base_dir, 'Downloads', 'Music')
cookie_file = os.path.join(base_dir, 'Downloads', 'Cookies', 'cookies.txt')

# Fortschrittsdaten
progress_data = {}

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def progress_hook(d):
    video_id = d.get('info_dict', {}).get('id', 'unknown')
    title = d.get('info_dict', {}).get('title', 'Unknown Title')

    if d['status'] == 'downloading':
        progress_data[video_id] = {
            "title": title,
            "status": "downloading",
            "progress": d.get('_percent_str', '0%').strip(),
            "speed": d.get('_speed_str', '0B/s'),
            "eta": d.get('_eta_str', '0s'),
            "last_update": time.time()
        }
    elif d['status'] == 'finished':
        progress_data[video_id] = {
            "title": title,
            "status": "finished",
            "progress": "100%",
            "message": "✅ Finished downloading",
            "last_update": time.time()
        }

def run_download(ydl_opts, url):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        progress_data['error'] = str(e)

@app.route('/')
def index():
    # HTML von Ihrer index.html Datei einbinden
    html_path = os.path.join(base_dir, 'templates', 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/download', methods=['POST'])
def download():
    urls = request.form['urls'].splitlines()
    download_type = request.form['type']

    try:
        # Verzeichnisse erstellen
        create_directory(base_dir)
        cookie_dir = os.path.dirname(cookie_file)
        create_directory(cookie_dir)
        if not os.path.exists(cookie_file):
            with open(cookie_file, 'w') as f:
                f.write('')

        for url in urls:
            url = url.strip()
            if not url:
                continue

            # Spotify separat behandeln
            if "spotify.com" in url:
                create_directory(download_path_music)
                subprocess.run(["spotdl", url, "--output", download_path_music], check=True)
                continue

            # YouTube / andere
            if download_type == 'mp4':
                create_directory(download_path_video)
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': os.path.join(download_path_video, '%(title)s [%(id)s].%(ext)s'),
                    'merge_output_format': 'mp4',
                    'noplaylist': True,
                    'cookiefile': cookie_file,
                    'progress_hooks': [progress_hook]
                }
                run_download(ydl_opts, url)

            elif download_type == 'mp3':
                create_directory(download_path_music)
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(download_path_music, '%(title)s [%(id)s].%(ext)s'),
                    'noplaylist': True,
                    'postprocessors': [
                        {
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '320',
                        }
                    ],
                    'cookiefile': cookie_file,
                    'progress_hooks': [progress_hook]
                }
                run_download(ydl_opts, url)

        return jsonify({"status": "success", "message": f"Downloaded {len(urls)} URLs successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/progress')
def progress():
    now = time.time()
    active = {
        vid: info for vid, info in progress_data.items()
        if (info["status"] == "downloading") or (now - info["last_update"] < 30)
    }
    return jsonify(active)

def run_server():
    app.run(port=5000, debug=False, threaded=True)

if __name__ == '__main__':
    # Server im Hintergrund starten
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Desktop App erstellen
    window = webview.create_window(
        'Video & Music Downloader',
        'http://127.0.0.1:5000',
        width=900,
        height=700,
        resizable=True,
        text_select=True
    )
    
    webview.start()