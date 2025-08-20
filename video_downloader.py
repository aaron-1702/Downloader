from flask import Flask, render_template, request, jsonify, Response
import yt_dlp
import os
import subprocess
import threading
import time
import queue
import webbrowser

app = Flask(__name__)

# Paths
base_dir = os.path.dirname(os.path.abspath(__file__))
download_path_video = os.path.join(base_dir, 'Downloads', 'Videos')
download_path_music = os.path.join(base_dir, 'Downloads', 'Music')
cookie_file = os.path.join(base_dir, 'Downloads', 'Cookies', 'cookies.txt')

progress_queue = queue.Queue()  # Queue for progress updates

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

progress_data = {}  # video_id -> infos

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

def update_status(video_id, title, message):
    progress_data[video_id] = {
        "title": title,
        "status": "retry",
        "message": message,
        "last_update": time.time()
    }

def run_download(ydl_opts, url):
    video_id = "unknown"
    title = url
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_id = info.get('id', 'unknown')
            title = info.get('title', url)
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "not available on this app" in error_msg:
            # Erster Fallback: nur Web-Client
            update_status(video_id, title, "🔄 Switching to Web client...")
            ydl_opts['extractor_args'] = {'youtube': ['player_client=web']}
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except yt_dlp.utils.DownloadError as e2:
                if "not available" in str(e2):
                    # Zweiter Fallback: Web, Android, iOS
                    update_status(video_id, title, "🔄 Switching to Web + Android + iOS...")
                    ydl_opts['extractor_args'] = {'youtube': ['player_client=web,android,ios']}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                else:
                    raise
        else:
            raise
        
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    urls = request.form['urls'].splitlines()
    download_type = request.form['type']

    try:
        # Create the parent 'Downloads' directory if it doesn't exist
        create_directory(base_dir)
        # Create the 'Cookies' directory and file if they don't exist
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
    # nur laufende / frische Downloads zurückgeben (max. 30 Sekunden alt)
    now = time.time()
    active = {
        vid: info for vid, info in progress_data.items()
        if (info["status"] == "downloading") or (now - info["last_update"] < 30)
    }
    return jsonify(active)

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True, threaded=True)




