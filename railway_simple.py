#!/usr/bin/env python3
"""
Simple Railway startup script - follows Railway web service patterns
"""
import os
import subprocess
import sys

def main():
    """Simple Railway-compatible startup"""
    
    # Get Railway port
    port = os.environ.get("PORT", "8501")
    
    print(f"🚀 Starting Railway Web Service on port {port}")
    
    # Standard Railway environment setup
    os.environ.update({
        "STREAMLIT_SERVER_PORT": port,
        "STREAMLIT_SERVER_ADDRESS": "0.0.0.0",
        "STREAMLIT_SERVER_HEADLESS": "true",
        "STREAMLIT_SERVER_ENABLE_CORS": "false",
        "STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION": "false"
    })
    
    # Create required directories
    for directory in ["input", "output", "temp", ".streamlit"]:
        os.makedirs(directory, exist_ok=True)
    
    # Simple streamlit command that Railway recognizes as web service
    cmd = [
        "streamlit", "run", "app.py",
        "--server.port", port,
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ]
    
    print(f"📍 Command: {' '.join(cmd)}")
    
    # Execute
    subprocess.run(cmd)

if __name__ == "__main__":
    main() 