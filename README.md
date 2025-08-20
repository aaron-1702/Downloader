# Downloader

Downloads music and videos from **YouTube, Instagram, TikTok, Spotify, and SoundCloud**.

## Easy Setup (Windows)

1.  **Right-click** on the `setup.ps1` file in the project folder.
2.  Select **"Run with PowerShell"**.
3.  Follow the instructions in the script. It will automatically install Scoop, FFmpeg, the Python libraries, and create the necessary folders.

> **Note:** Windows might show a security warning. Select "Run anyway" or "Yes" to execute the script.

## Manual Setup

### Install Python Libraries
Use `pip` to install the required libraries:

```bash
pip install -r requirements.txt
```

### Install FFmpeg (via Scoop)
FFmpeg is required to merge video and audio formats.

1. If you don't have Scoop installed, install it first:

```powershell
iwr -useb get.scoop.sh | iex
```

2. Then install FFmpeg:

```powershell
scoop install ffmpeg
```

#### Verify Installation
After installation, check that FFmpeg is accessible:

```powershell
ffmpeg -version
```

## Save your Cookies
To access certain data, export cookies from your browser using an extension and save them as `cookies.txt` in the appropriate folder (`Downloads/Cookies/` relative to the script).

## Usage 

### Website

1.  Ensure the setup is complete and your `cookies.txt` file is in place.
2.  Run the application:
    ```bash
    python video_downloader.py
    ```
3.  Your browser should open automatically to `http://127.0.0.1:5000`.
4.  Paste one or more URLs into the textbox (one per line).
5.  Select either **MP4 (Video)** or **MP3 (Audio)**.
6.  Click **"Start Download"**. The progress will be shown on the page.

### Desktop-Application

1. Double-click on `start_app.bat`
- The application opens immediately as a standalone window
- Works exactly the same as the web version



## Folder Structure
All downloaded files and cookies are stored inside subfolders of the project directory:

```
Downloader-main/
│
├── Downloads/
│   ├── Videos/         # Downloaded MP4 files are saved here
│   ├── Music/          # Downloaded MP3 files are saved here
│   └── Cookies/
│       └── cookies.txt # Your browser cookies file (manually added)
├── templates/
│   └── index.html     # The web interface
├── downloader_app.py   # Desktop application version (PyWebView)
├── video_downloader.py   # The main application script
├── requirements.txt    # Python dependency list
├── setup.ps1          # Automated Windows setup script
├── start_app.bat       # Batch file to launch desktop app
└── README.md          # This file
```
## Supported Services

-   YouTube
-   Instagram
-   TikTok
-   Spotify (via spotdl)
-   SoundCloud
