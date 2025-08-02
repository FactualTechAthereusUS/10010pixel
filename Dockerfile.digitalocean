# DigitalOcean-specific Dockerfile for video processing app
FROM python:3.11.7-slim

# Set working directory
WORKDIR /app

# Install system dependencies for video processing
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 libfontconfig1 libxrender1 libgl1-mesa-glx git curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p input output temp .streamlit

# Set environment variables for DigitalOcean
ENV DIGITALOCEAN=true
ENV PLATFORM=digitalocean
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Expose port 8080 for DigitalOcean
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run the DigitalOcean startup script
CMD ["python", "digitalocean_start.py"]