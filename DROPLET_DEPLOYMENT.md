# 🚀 DigitalOcean Droplet Deployment Guide

## **Why Droplet vs App Platform?**

| Feature | App Platform | **Droplet (Recommended)** |
|---------|-------------|---------------------------|
| **File Upload Limit** | 500MB (60s timeout) | **1000MB+ (no timeouts)** |
| **Server Control** | Limited | **Full root access** |
| **Performance** | Good | **Maximum** |
| **Cost** | $24-48/month | **$24-48/month** |
| **Setup Complexity** | Easy | **Medium (automated)** |

## **📊 Recommended Droplet Specs:**

### **🎯 RECOMMENDED: CPU-Optimized**
- **Size**: 4 vCPUs, 8GB RAM
- **Storage**: 160GB SSD
- **Cost**: $48/month
- **Why**: Video processing is CPU/RAM intensive

### **💰 Budget Option: Regular**
- **Size**: 2 vCPUs, 4GB RAM  
- **Storage**: 80GB SSD
- **Cost**: $24/month
- **Why**: Works for smaller videos, slower processing

## **🚀 AUTOMATED DEPLOYMENT:**

### **Step 1: Create Droplet**
1. Go to [DigitalOcean Droplets](https://cloud.digitalocean.com/droplets)
2. **Create Droplet**
3. **Image**: Ubuntu 22.04 LTS
4. **Size**: CPU-Optimized 4GB ($48/month) or Regular 4GB ($24/month)
5. **Authentication**: SSH Key (recommended) or Password
6. **Create Droplet**

### **Step 2: Clone & Deploy** 
SSH into your droplet and run:

```bash
# Clone the repository
git clone https://github.com/FactualTechAthereusUS/10010pixel.git
cd 10010pixel

# Run automated deployment (as root)
sudo python3 droplet_setup.py
```

**That's it!** The script automatically:
- ✅ Installs all system dependencies (FFmpeg, OpenCV, Nginx)
- ✅ Sets up Python environment
- ✅ Configures Nginx reverse proxy with large file support
- ✅ Creates systemd service for auto-start
- ✅ Optimizes for 1000MB+ video uploads

### **Step 3: Access Your App**
```
🌐 Your app: http://YOUR_DROPLET_IP
📊 Upload limit: 1000MB
⚡ Processing: Maximum performance
```

## **🔧 Manual Commands:**

```bash
# Check service status
sudo systemctl status video-processor

# View logs
sudo journalctl -u video-processor -f

# Restart service
sudo systemctl restart video-processor

# Check Nginx status
sudo systemctl status nginx

# Test Nginx config
sudo nginx -t
```

## **🌐 Custom Domain Setup:**

1. **Point your domain to Droplet IP**:
   ```
   A record: @ -> YOUR_DROPLET_IP
   A record: www -> YOUR_DROPLET_IP
   ```

2. **Update Nginx for your domain**:
   ```bash
   sudo nano /etc/nginx/sites-available/video-processor
   # Change: server_name _;
   # To: server_name yourdomain.com www.yourdomain.com;
   
   sudo systemctl restart nginx
   ```

3. **Add SSL (optional)**:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

## **🚀 Performance Optimizations:**

### **Droplet Advantages:**
- ✅ **No 60-second timeouts** (can process 2GB+ videos)
- ✅ **Full server control** (optimize everything)
- ✅ **8 CPU threads** (vs 4-6 on App Platform)
- ✅ **3GB RAM** for video processing (vs 1.5GB)
- ✅ **Custom Nginx config** (1000MB uploads, 30min timeouts)
- ✅ **Direct file system** (faster I/O)

### **Expected Performance:**
- **100MB video**: ~30-45 seconds
- **500MB video**: ~2-3 minutes  
- **1000MB video**: ~4-6 minutes
- **Multiple files**: Parallel processing

## **🔍 Troubleshooting:**

### **Service won't start:**
```bash
sudo journalctl -u video-processor --no-pager
```

### **Nginx errors:**
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

### **Upload fails:**
```bash
# Check disk space
df -h

# Check memory
free -h

# Check service
sudo systemctl status video-processor
```

### **Domain not working:**
```bash
# Check DNS
nslookup yourdomain.com

# Check Nginx config
sudo nginx -t
```

## **🔄 Updates:**

```bash
# Update app code
cd /root/10010pixel  # or wherever you cloned
git pull origin main

# Restart service
sudo systemctl restart video-processor
```

## **💡 Pro Tips:**

1. **Use CPU-Optimized Droplets** for video processing
2. **Monitor resource usage** with `htop`
3. **Regular backups** of processed videos
4. **Use SSH keys** for better security
5. **Set up monitoring** for production use

---

**🎯 Result: 1000MB video uploads with maximum performance and no timeout issues!**