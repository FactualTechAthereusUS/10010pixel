#!/usr/bin/env python3
"""
DigitalOcean-specific startup script for Streamlit app
Optimized for DigitalOcean App Platform
"""
import os
import subprocess
import sys
import time

def main():
    """Start the Streamlit app with DigitalOcean-optimized settings"""
    
    # Get port from DigitalOcean environment
    port = os.environ.get("PORT", "8080")
    
    # DigitalOcean-specific environment setup
    os.environ["STREAMLIT_SERVER_PORT"] = port
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    
    # Create necessary directories
    for dir_name in ["input", "output", "temp", ".streamlit"]:
        os.makedirs(dir_name, exist_ok=True)
    
    # Create optimized .streamlit/config.toml for DigitalOcean
    config_content = f"""[server]
port = {port}
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 200

[browser]
gatherUsageStats = false

[theme]
base = "dark"
"""
    
    with open(".streamlit/config.toml", "w") as f:
        f.write(config_content)
    
    # Build the streamlit command optimized for DigitalOcean
    cmd = [
        "streamlit", "run", "app.py",
        "--server.port", port,
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--browser.gatherUsageStats", "false"
    ]
    
    print(f"🚀 Starting Streamlit on DigitalOcean (port {port})...")
    print(f"📍 Command: {' '.join(cmd)}")
    print(f"💾 Available memory: Better than Railway!")
    print(f"📁 Max upload size: 200MB")
    
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