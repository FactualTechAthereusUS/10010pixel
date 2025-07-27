#!/usr/bin/env python3
"""
Railway fallback startup script with enhanced debugging
"""
import os
import subprocess
import sys
import time
import socket

def check_port_available(port):
    """Check if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', int(port)))
            return True
    except:
        return False

def main():
    """Start with enhanced debugging"""
    
    print("🔍 Railway Startup Debug Information")
    print("=" * 50)
    
    # Environment debug
    port = os.environ.get("PORT", "8501")
    print(f"📍 PORT from environment: {port}")
    print(f"📍 Working directory: {os.getcwd()}")
    print(f"📍 Python executable: {sys.executable}")
    
    # Check if port is available
    if check_port_available(port):
        print(f"✅ Port {port} is available")
    else:
        print(f"❌ Port {port} is NOT available")
    
    # Create directories with verbose output
    print("\n📁 Creating directories...")
    for dir_name in ["input", "output", "temp", ".streamlit"]:
        try:
            os.makedirs(dir_name, exist_ok=True)
            print(f"✅ Created/verified: {dir_name}/")
        except Exception as e:
            print(f"❌ Failed to create {dir_name}/: {e}")
    
    # Check if streamlit is available
    print("\n🔍 Checking Streamlit installation...")
    try:
        result = subprocess.run(['streamlit', '--version'], capture_output=True, text=True)
        print(f"✅ Streamlit version: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Streamlit not found: {e}")
        sys.exit(1)
    
    # Check if app.py exists
    if os.path.exists('app.py'):
        print("✅ app.py found")
    else:
        print("❌ app.py not found!")
        sys.exit(1)
    
    # Try multiple startup methods
    startup_methods = [
        # Method 1: Full configuration
        [
            "streamlit", "run", "app.py",
            "--server.port", port,
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
            "--browser.gatherUsageStats", "false"
        ],
        # Method 2: Minimal configuration
        [
            "streamlit", "run", "app.py",
            "--server.port", port,
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ],
        # Method 3: Default Railway method
        [
            "streamlit", "run", "app.py"
        ]
    ]
    
    for i, cmd in enumerate(startup_methods, 1):
        print(f"\n🚀 Trying startup method {i}...")
        print(f"📍 Command: {' '.join(cmd)}")
        
        try:
            # Set environment variables for this attempt
            env = os.environ.copy()
            env['STREAMLIT_SERVER_PORT'] = port
            env['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
            env['STREAMLIT_SERVER_HEADLESS'] = 'true'
            
            # Start the process
            process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            # Wait a few seconds and check if it's still running
            time.sleep(3)
            if process.poll() is None:  # Still running
                print(f"✅ Method {i} appears to be working!")
                # Continue running
                process.wait()
                break
            else:
                print(f"❌ Method {i} failed quickly")
                if process.stdout:
                    output = process.stdout.read()
                    print(f"Output: {output}")
                    
        except Exception as e:
            print(f"❌ Method {i} failed: {e}")
            continue
    
    print("❌ All startup methods failed!")
    sys.exit(1)

if __name__ == "__main__":
    main() 