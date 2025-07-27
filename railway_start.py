#!/usr/bin/env python3
"""
Railway-specific startup script for Streamlit app
"""
import os
import subprocess
import sys
import time

def main():
    """Start the Streamlit app with Railway-optimized settings"""
    
    # Get port from Railway environment
    port = os.environ.get("PORT", "8501")
    
    # Railway-specific environment setup
    os.environ["STREAMLIT_SERVER_PORT"] = port
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    
    # Create necessary directories
    for dir_name in ["input", "output", "temp", ".streamlit"]:
        os.makedirs(dir_name, exist_ok=True)
    
    # Build the streamlit command
    cmd = [
        "streamlit", "run", "app.py",
        "--server.port", port,
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--browser.gatherUsageStats", "false"
    ]
    
    print(f"🚀 Starting Streamlit on Railway (port {port})...")
    print(f"📍 Command: {' '.join(cmd)}")
    
    # Start the app
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Shutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main() 