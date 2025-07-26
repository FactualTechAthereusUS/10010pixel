@echo off
echo 🎬 TikTok Video Processor
echo =========================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.7 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ❌ FFmpeg is not installed. Please install FFmpeg first:
    echo.
    echo Download from: https://ffmpeg.org/download.html
    echo Add ffmpeg.exe to your system PATH
    echo.
    pause
    exit /b 1
)

REM Install dependencies
if exist requirements.txt (
    echo 📦 Installing Python dependencies...
    pip install -r requirements.txt
)

REM Create directories
if not exist "input" mkdir input
if not exist "output" mkdir output
if not exist "temp" mkdir temp

echo.
echo 🚀 Starting TikTok Video Processor...
echo 🌐 Opening in browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server.
echo.

REM Run the Streamlit app
streamlit run app.py

pause 