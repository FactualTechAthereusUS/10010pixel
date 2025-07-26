#!/usr/bin/env python3
"""
Startup script for Railway deployment
"""
import os
import subprocess
import sys

def main():
    # Get port from environment variable or default to 8501
    port = os.environ.get('PORT', '8501')
    
    # Streamlit command
    cmd = [
        'streamlit', 'run', 'app.py',
        '--server.port', port,
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--browser.gatherUsageStats', 'false'
    ]
    
    print(f"Starting Streamlit on port {port}...")
    subprocess.run(cmd)

if __name__ == "__main__":
    main() 