Write-Host "=== Downloader Setup Script ===" -ForegroundColor Green
Write-Host "This script will install Scoop, FFmpeg, and the required Python libraries." -ForegroundColor Yellow
Write-Host ""

# Check if Scoop is installed
if (Get-Command scoop -ErrorAction SilentlyContinue) {
    Write-Host "✅ Scoop is already installed." -ForegroundColor Green
} else {
    Write-Host "Installing Scoop package manager..." -ForegroundColor Yellow
    try {
        # Run the Scoop installer
        Invoke-RestMethod get.scoop.sh | Invoke-Expression
        Write-Host "✅ Scoop installed successfully." -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install Scoop. Error: $_" -ForegroundColor Red
        Write-Host "Please try installing Scoop manually from https://scoop.sh"
        pause
        exit 1
    }
}

# Check if FFmpeg is installed via Scoop
if (scoop list ffmpeg -e) {
    Write-Host "✅ FFmpeg is already installed." -ForegroundColor Green
} else {
    Write-Host "Installing FFmpeg (this is required for video/audio processing)..." -ForegroundColor Yellow
    try {
        scoop install ffmpeg
        Write-Host "✅ FFmpeg installed successfully." -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install FFmpeg. Error: $_" -ForegroundColor Red
        Write-Host "Please try installing FFmpeg manually: 'scoop install ffmpeg'"
        pause
        exit 1
    }
}

# Install Python dependencies
Write-Host "Installing required Python libraries (Flask, yt-dlp, spotdl)..." -ForegroundColor Yellow
try {
    pip install -U -r requirements.txt
    Write-Host "✅ Python libraries installed successfully." -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install Python libraries. Error: $_" -ForegroundColor Red
    Write-Host "Please try installing them manually: 'pip install -r requirements.txt'"
    pause
    exit 1
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Place your 'cookies.txt' file in the 'Downloads/Cookies/' folder." -ForegroundColor White
Write-Host "2. Run the application: 'python video_downloader.py'" -ForegroundColor White
Write-Host "3. The browser should open automatically." -ForegroundColor White
Write-Host "==================================================" -ForegroundColor Green
pause
