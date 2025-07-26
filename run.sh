#!/bin/bash

echo "🎬 TikTok Video Processor"
echo "========================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg is not installed. Please install FFmpeg first:"
    echo ""
    echo "macOS: brew install ffmpeg"
    echo "Ubuntu/Debian: sudo apt install ffmpeg"
    echo "Windows: Download from https://ffmpeg.org/download.html"
    echo ""
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Create directories
mkdir -p input output temp

echo "🚀 Starting TikTok Video Processor..."
echo "🌐 Opening in browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

# Run the Streamlit app in virtual environment
source venv/bin/activate
streamlit run app.py 