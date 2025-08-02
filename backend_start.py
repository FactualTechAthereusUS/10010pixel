#!/usr/bin/env python3
"""
DigitalOcean Backend Startup Script
Starts the FastAPI backend with optimized settings
"""
import os
import sys
import uvicorn

def main():
    """Start the FastAPI backend"""
    
    # Get port from DigitalOcean environment
    port = int(os.environ.get("PORT", 8080))
    
    # Set environment variables for optimization
    os.environ["DIGITALOCEAN"] = "true"
    os.environ["PLATFORM"] = "digitalocean"
    
    # Create necessary directories
    for dir_name in ["api_input", "api_output", "api_temp"]:
        os.makedirs(dir_name, exist_ok=True)
    
    print(f"🚀 Starting FastAPI Backend on DigitalOcean (port {port})...")
    print(f"📍 Platform: DigitalOcean")
    print(f"💾 Memory optimized for video processing")
    print(f"🔧 Hardware acceleration enabled")
    
    # Start the FastAPI app with uvicorn
    try:
        uvicorn.run(
            "backend_api:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            workers=1,
            access_log=True
        )
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Shutting down backend...")
        sys.exit(0)

if __name__ == "__main__":
    main()