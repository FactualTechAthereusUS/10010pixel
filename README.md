# TikTok Video Processor

A desktop app that processes videos to create unique digital fingerprints, helping avoid duplicate content detection when uploading to TikTok.

## Features

✅ **Metadata Stripping** - Removes all video metadata using FFmpeg  
✅ **Invisible Pixel Noise** - Adds imperceptible pixel variations using OpenCV  
✅ **Video Re-encoding** - Changes compression settings to alter file signature  
✅ **Silence Padding** - Optionally adds silence at start/end  
✅ **Transparent Overlay** - Adds 1px transparent overlay in random corners  
✅ **Randomized Filenames** - Generates unique output filenames  
✅ **Batch Processing** - Process multiple videos simultaneously  

## Prerequisites

### 1. Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Add to system PATH

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 2. Verify FFmpeg Installation
```bash
ffmpeg -version
```

## Setup

### 1. Clone/Download
Download or clone this project to your local machine.

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Usage

### 1. Configure Processing Options
Use the sidebar to select which transformations to apply:

- **Strip Metadata** ✅ (Recommended) - Removes all video metadata
- **Add Pixel Noise** ✅ (Recommended) - Adds invisible pixel variations
- **Re-encode Video** ✅ (Recommended) - Changes compression settings
- **Add Silence Padding** - Adds 0.1-1.0 seconds of silence
- **Add Transparent Overlay** - Adds 1px transparent overlay

### 2. Upload Videos
- Click "Choose video files" or drag & drop
- Supports: MP4, AVI, MOV, MKV, WEBM
- Can process multiple videos at once

### 3. Process Videos
- Click "🚀 Start Processing"
- Monitor progress in real-time
- View results and any error messages

### 4. Access Output
- Processed videos are saved to the `output/` folder
- Each video gets a randomized filename like `vid_abc123def456_789012.mp4`
- Click "🔄 Refresh Output List" to see all processed files

## How It Works

The app applies multiple transformations to alter the video's digital fingerprint:

1. **Metadata Removal** - Strips EXIF and other identifying data
2. **Pixel Noise Addition** - Modifies ~0.5% of pixels by ±1-2 values (imperceptible to human eye)
3. **Re-encoding** - Changes compression parameters (CRF, preset, codec settings)
4. **Audio Padding** - Randomly adds silence to beginning or end
5. **Visual Overlay** - Places 1px transparent element in random corner

These changes alter the video's hash without affecting visual quality, making each output unique.

## Directory Structure

```
project/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── input/             # Input videos (auto-created)
├── output/            # Processed videos (auto-created)
└── temp/              # Temporary processing files (auto-created)
```

## Troubleshooting

### FFmpeg Not Found
- Ensure FFmpeg is installed and added to system PATH
- Test with `ffmpeg -version` in terminal

### Memory Issues
- Process fewer videos at once
- Lower CRF value (higher compression)
- Close other applications

### Processing Failures
- Check video file isn't corrupted
- Ensure sufficient disk space
- Try processing one video at a time

### Slow Processing
- Use higher CRF values (faster, smaller files)
- Disable unnecessary processing options
- Process shorter videos first

## Technical Details

- **Frontend**: Streamlit web interface
- **Video Processing**: OpenCV + FFmpeg
- **Noise Algorithm**: Random pixel modification with Gaussian distribution
- **File Handling**: Temporary processing pipeline with cleanup
- **Output**: Randomized filenames to avoid naming conflicts

## Security & Privacy

- All processing happens locally on your machine
- No data is sent to external servers
- Temporary files are automatically cleaned up
- Original files remain unchanged

---

**Note**: This tool is designed for legitimate content repurposing. Ensure you comply with platform terms of service and copyright laws. 