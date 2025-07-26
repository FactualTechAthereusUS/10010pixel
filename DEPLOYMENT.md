# Railway Deployment Guide

## 🚀 Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

## 📋 Prerequisites

- Railway account
- Git repository with this code
- FFmpeg support (handled automatically by Railway)

## 🔧 Deployment Files

This project includes all necessary files for Railway deployment:

- `Procfile` - Web process definition
- `railway.toml` - Railway configuration
- `nixpacks.toml` - Build configuration with FFmpeg
- `start.py` - Alternative startup script
- `Dockerfile` - Docker deployment option
- `.streamlit/config.toml` - Streamlit production config

## 📦 Environment Variables

Railway will automatically handle:
- `PORT` - Server port (Railway managed)
- `RAILWAY_ENVIRONMENT` - Production environment

## 🏗️ Build Process

1. Railway detects Python project
2. Installs system dependencies (FFmpeg, OpenCV libs)
3. Installs Python dependencies from `requirements.txt`
4. Creates necessary directories (`temp/`, `output/`, `input/`)
5. Starts Streamlit app on Railway's assigned port

## 🌐 Post-Deployment

After deployment:
- App runs at your Railway-provided URL
- Automatic HTTPS
- Health checks enabled
- Auto-scaling based on usage

## 🔍 Troubleshooting

**Build fails:** Check logs for missing dependencies
**App crashes:** Verify FFmpeg is installed (should be automatic)
**Upload issues:** Ensure temp directories are writable

## 🛠️ Local Testing

Test production build locally:
```bash
# Install dependencies
pip install -r requirements.txt

# Run with production settings
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
```

## 📈 Performance

- Hardware acceleration auto-detected
- Multi-threaded video processing
- Optimized for Railway's infrastructure
- Handles multiple concurrent users 