#!/usr/bin/env python3
"""
DigitalOcean Backend Startup Script
Starts the FastAPI backend with optimized settings
"""
import os
import sys
import uvicorn

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg is available")
        else:
            print("❌ FFmpeg not available")
            return False
    except Exception as e:
        print(f"❌ FFmpeg check failed: {e}")
        return False
    
    return True

def main():
    """Start the FastAPI backend"""
    
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        print("❌ Dependency check failed")
        sys.exit(1)
    
    # Get port from DigitalOcean environment
    port = int(os.environ.get("PORT", 8080))
    
    # Set environment variables for optimization
    os.environ["DIGITALOCEAN"] = "true"
    os.environ["PLATFORM"] = "digitalocean"
    
    # Create necessary directories
    for dir_name in ["api_input", "api_output", "api_temp"]:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ Created directory: {dir_name}")
    
    print(f"🚀 Starting FastAPI Backend on DigitalOcean (port {port})...")
    print(f"📍 Platform: DigitalOcean")
    print(f"💾 Memory optimized for video processing")
    print(f"🔧 Hardware acceleration enabled")
    
    # Import the app here to catch import errors
    try:
        from backend_api import app
        print("✅ FastAPI app imported successfully")
    except Exception as e:
        print(f"❌ Failed to import FastAPI app: {e}")
        sys.exit(1)
    
    # Start the FastAPI app with uvicorn
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            reload=False,
            workers=1,
            access_log=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Shutting down backend...")
        sys.exit(0)

if __name__ == "__main__":
    main()