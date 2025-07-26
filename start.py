#!/usr/bin/env python3
"""
Production startup script for Railway deployment
"""
import os
import subprocess
import sys

def main():
    port = os.environ.get("PORT", "8501")
    
    cmd = [
        "streamlit", "run", "app.py",
        "--server.port", port,
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--browser.gatherUsageStats", "false"
    ]
    
    print(f"Starting Streamlit on port {port}...")
    subprocess.run(cmd)

if __name__ == "__main__":
    main() 