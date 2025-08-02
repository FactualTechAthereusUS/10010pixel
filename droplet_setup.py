#!/usr/bin/env python3
"""
DigitalOcean Droplet deployment script for video processing app
Optimized for direct server deployment (not App Platform)
"""
import os
import subprocess
import sys
import time

def install_system_dependencies():
    """Install system dependencies for video processing"""
    print("🔧 Installing system dependencies...")
    
    # Update package list
    subprocess.run(["sudo", "apt", "update"], check=True)
    
    # Install required packages
    packages = [
        "python3-pip",
        "python3-venv", 
        "ffmpeg",
        "libsm6",
        "libxext6", 
        "libfontconfig1",
        "libxrender1",
        "libgl1-mesa-glx",
        "nginx",
        "git",
        "curl",
        "htop"
    ]
    
    subprocess.run(["sudo", "apt", "install", "-y"] + packages, check=True)
    print("✅ System dependencies installed")

def setup_python_environment():
    """Set up Python virtual environment"""
    print("🐍 Setting up Python environment...")
    
    # Create virtual environment
    subprocess.run(["python3", "-m", "venv", "venv"], check=True)
    
    # Activate and install requirements
    subprocess.run(["./venv/bin/pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run(["./venv/bin/pip", "install", "-r", "requirements.txt"], check=True)
    
    print("✅ Python environment ready")

def setup_nginx():
    """Configure Nginx reverse proxy"""
    print("🌐 Configuring Nginx...")
    
    nginx_config = """
server {
    listen 80;
    server_name _;
    
    # Large file upload support
    client_max_body_size 1000M;
    client_body_timeout 300s;
    client_header_timeout 300s;
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Large file and timeout support
        proxy_read_timeout 1800s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_request_buffering off;
        proxy_buffering off;
    }
    
    # WebSocket support for Streamlit
    location /_stcore/stream {
        proxy_pass http://127.0.0.1:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
"""
    
    # Write Nginx config
    with open("/tmp/video-processor", "w") as f:
        f.write(nginx_config)
    
    # Move to sites-available and enable
    subprocess.run(["sudo", "mv", "/tmp/video-processor", "/etc/nginx/sites-available/"], check=True)
    subprocess.run(["sudo", "ln", "-sf", "/etc/nginx/sites-available/video-processor", "/etc/nginx/sites-enabled/"], check=True)
    
    # Remove default site
    subprocess.run(["sudo", "rm", "-f", "/etc/nginx/sites-enabled/default"], check=True)
    
    # Test and restart Nginx
    subprocess.run(["sudo", "nginx", "-t"], check=True)
    subprocess.run(["sudo", "systemctl", "restart", "nginx"], check=True)
    subprocess.run(["sudo", "systemctl", "enable", "nginx"], check=True)
    
    print("✅ Nginx configured")

def setup_systemd_service():
    """Create systemd service for auto-start"""
    print("⚙️ Setting up systemd service...")
    
    app_dir = os.getcwd()
    
    service_content = f"""[Unit]
Description=Video Processor Streamlit App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={app_dir}
Environment=PATH={app_dir}/venv/bin
Environment=PLATFORM=droplet
Environment=STREAMLIT_SERVER_HEADLESS=true
Environment=STREAMLIT_SERVER_ENABLE_CORS=false
Environment=STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
ExecStart={app_dir}/venv/bin/streamlit run app.py --server.port=8501 --server.address=127.0.0.1 --server.headless=true --server.maxUploadSize=1000 --server.maxMessageSize=1000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
    
    # Write service file
    with open("/tmp/video-processor.service", "w") as f:
        f.write(service_content)
    
    # Install service
    subprocess.run(["sudo", "mv", "/tmp/video-processor.service", "/etc/systemd/system/"], check=True)
    subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
    subprocess.run(["sudo", "systemctl", "enable", "video-processor"], check=True)
    
    print("✅ Systemd service created")

def main():
    """Main deployment function"""
    print("🚀 DROPLET DEPLOYMENT STARTING...")
    print("=" * 50)
    
    try:
        # Check if running as root
        if os.geteuid() != 0:
            print("❌ Please run as root: sudo python3 droplet_setup.py")
            sys.exit(1)
        
        # Installation steps
        install_system_dependencies()
        setup_python_environment() 
        setup_nginx()
        setup_systemd_service()
        
        # Create directories
        for directory in ["input", "output", "temp", ".streamlit"]:
            os.makedirs(directory, exist_ok=True)
        
        # Start the service
        subprocess.run(["sudo", "systemctl", "start", "video-processor"], check=True)
        
        print("\n" + "=" * 50)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("=" * 50)
        print(f"🌐 Your app is running at: http://YOUR_DROPLET_IP")
        print("📊 Service status: sudo systemctl status video-processor")
        print("📋 Service logs: sudo journalctl -u video-processor -f")
        print("🔄 Restart service: sudo systemctl restart video-processor")
        print("\n✅ 500MB video uploads are now supported!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()