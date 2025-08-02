#!/usr/bin/env python3
"""
Railway Frontend - Streamlit UI that calls DigitalOcean backend
This is the user-facing interface that handles uploads and displays results
"""
import streamlit as st
import requests
import time
import json
import os
from pathlib import Path
import tempfile
from typing import Optional

# Configure page
st.set_page_config(
    page_title="AURA FARMING - Video Processor",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for responsive design (same as original)
st.markdown("""
<style>
    /* Main container responsive adjustments */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        /* Adjust title size for mobile */
        h1 {
            font-size: 1.8rem !important;
            text-align: center;
        }
        
        /* Make buttons full width on mobile */
        .stButton > button {
            width: 100% !important;
            margin-bottom: 0.5rem;
        }
        
        /* Stack columns vertically on mobile */
        .row-widget.stHorizontal {
            flex-direction: column;
        }
    }
    
    /* General UI improvements */
    .stSelectbox > div > div {
        background-color: #2a2a2a !important;
        color: white !important;
        border-radius: 6px;
        border: 1px solid #444444 !important;
    }
    
    .stFileUploader > div {
        background-color: #1a1a1a !important;
        border: 2px dashed #444444 !important;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
    }
    
    /* Progress bar styling */
    .stProgress .progress-bar {
        background-color: #00cc88;
        border-radius: 4px;
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background-color: #0066cc;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stDownloadButton > button:hover {
        background-color: #0052a3;
        transform: translateY(-1px);
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
BACKEND_URL = os.environ.get("BACKEND_URL", "https://your-digitalocean-app.ondigitalocean.app")
BACKEND_URL = BACKEND_URL.rstrip("/")  # Remove trailing slash

class BackendAPI:
    """Client for communicating with DigitalOcean backend"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
    
    def check_health(self) -> bool:
        """Check if backend is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/")
            return response.status_code == 200
        except:
            return False
    
    def get_status(self) -> dict:
        """Get backend system status"""
        try:
            response = self.session.get(f"{self.base_url}/status")
            return response.json() if response.status_code == 200 else {}
        except:
            return {}
    
    def upload_video(self, file_data: bytes, filename: str) -> Optional[str]:
        """Upload video and return job ID"""
        try:
            files = {"file": (filename, file_data, "video/mp4")}
            response = self.session.post(f"{self.base_url}/upload", files=files)
            
            if response.status_code == 200:
                return response.json().get("job_id")
            else:
                st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")
                return None
        except Exception as e:
            st.error(f"Upload error: {str(e)}")
            return None
    
    def process_video(self, job_id: str, options: dict) -> bool:
        """Start video processing"""
        try:
            response = self.session.post(f"{self.base_url}/process/{job_id}", json=options)
            return response.status_code == 200
        except Exception as e:
            st.error(f"Processing error: {str(e)}")
            return False
    
    def get_job_status(self, job_id: str) -> dict:
        """Get job processing status"""
        try:
            response = self.session.get(f"{self.base_url}/job/{job_id}")
            return response.json() if response.status_code == 200 else {}
        except:
            return {}
    
    def download_video(self, filename: str) -> Optional[bytes]:
        """Download processed video"""
        try:
            response = self.session.get(f"{self.base_url}/download/{filename}")
            return response.content if response.status_code == 200 else None
        except:
            return None

def main():
    """Main Streamlit application"""
    
    # Header
    st.title("AURA FARMING")
    st.title("🎬 TikTok Video Processor")
    st.markdown("Create unique digital fingerprints to avoid duplicate content detection")
    
    # Backend URL configuration
    with st.sidebar:
        st.header("⚙️ Backend Configuration")
        backend_url = st.text_input(
            "Backend URL", 
            value=BACKEND_URL,
            help="DigitalOcean backend API URL"
        )
        
        if backend_url != BACKEND_URL:
            st.session_state.backend_url = backend_url
        else:
            st.session_state.backend_url = BACKEND_URL
    
    # Initialize API client
    api = BackendAPI(st.session_state.backend_url)
    
    # Backend health check
    if api.check_health():
        backend_status = api.get_status()
        st.success(f"✅ **Connected to DigitalOcean Backend**")
        
        # Show backend info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Platform", backend_status.get("platform", "Unknown").title())
        with col2:
            st.metric("Hardware Encoder", backend_status.get("hardware_encoder", "Unknown"))
        with col3:
            st.metric("Max Threads", backend_status.get("max_threads", "Unknown"))
    else:
        st.error("❌ **Cannot connect to backend**")
        st.error(f"Backend URL: {st.session_state.backend_url}")
        st.info("💡 **Setup Instructions:**")
        st.info("1. Deploy the backend_api.py to DigitalOcean")
        st.info("2. Update the BACKEND_URL in the sidebar")
        st.info("3. Make sure the backend is running and accessible")
        st.stop()
    
    st.info("📋 **Upload Limits**: Max 200MB per file | Supported: MP4, AVI, MOV, MKV, WEBM | Processed on DigitalOcean")
    
    # Processing options sidebar
    st.sidebar.header("Processing Options")
    
    options = {
        'strip_metadata': st.sidebar.checkbox("Strip Metadata", value=True, help="Remove all video metadata"),
        'add_noise': st.sidebar.checkbox("Add Pixel Noise", value=True, help="Add imperceptible pixel variations"),
        're_encode': st.sidebar.checkbox("Re-encode Video", value=True, help="Change encoding parameters"),
    }
    
    # Additional settings
    if options['add_noise']:
        options['noise_intensity'] = st.sidebar.slider("Noise Intensity", 1, 5, 2, help="Higher = more variation (still imperceptible)")
    
    if options['re_encode']:
        options['crf_value'] = st.sidebar.slider("CRF Value", 18, 35, 27, help="Lower = higher quality, larger file")
    
    # Main interface
    is_mobile = st.sidebar.checkbox("📱 Mobile Layout", value=False)
    
    if is_mobile:
        # Single column layout for mobile
        st.header("📤 Upload Videos")
        uploaded_files = st.file_uploader(
            "Choose video files",
            type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
            accept_multiple_files=True,
            help="Upload one or more video files to process"
        )
        
        if uploaded_files:
            st.markdown("### 📊 Upload Statistics")
            stats_col1, stats_col2 = st.columns(2)
            with stats_col1:
                st.metric("Files Selected", len(uploaded_files))
            with stats_col2:
                total_size = sum(file.size for file in uploaded_files)
                st.metric("Total Size", f"{total_size / (1024*1024):.1f} MB")
    else:
        # Desktop layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.header("📤 Upload Videos")
            uploaded_files = st.file_uploader(
                "Choose video files",
                type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
                accept_multiple_files=True,
                help="Upload one or more video files to process"
            )
        
        with col2:
            st.header("📊 Statistics")
            if uploaded_files:
                st.metric("Files Selected", len(uploaded_files))
                total_size = sum(file.size for file in uploaded_files)
                st.metric("Total Size", f"{total_size / (1024*1024):.1f} MB")
            else:
                st.info("No files selected")
                st.caption("Upload videos to see statistics")
    
    # Process videos
    if uploaded_files and st.button("🚀 Start Processing", type="primary", use_container_width=True):
        
        # Validate files
        valid_files = []
        for uploaded_file in uploaded_files:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            
            if file_size_mb > 200:
                st.error(f"❌ **{uploaded_file.name}**: Too large ({file_size_mb:.1f}MB, max 200MB)")
                continue
            
            if not uploaded_file.name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                st.error(f"❌ **{uploaded_file.name}**: Unsupported file type")
                continue
            
            valid_files.append(uploaded_file)
        
        if not valid_files:
            st.error("No valid files to process")
            st.stop()
        
        # Process each file
        results = []
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        for i, uploaded_file in enumerate(valid_files):
            status_placeholder.info(f"📤 Uploading {uploaded_file.name}...")
            
            # Upload file
            file_data = uploaded_file.getvalue()
            job_id = api.upload_video(file_data, uploaded_file.name)
            
            if not job_id:
                results.append(f"❌ {uploaded_file.name}: Upload failed")
                continue
            
            status_placeholder.info(f"⚙️ Processing {uploaded_file.name}...")
            
            # Start processing
            if not api.process_video(job_id, options):
                results.append(f"❌ {uploaded_file.name}: Processing failed to start")
                continue
            
            # Wait for completion
            max_wait_time = 600  # 10 minutes
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                job_status = api.get_job_status(job_id)
                status = job_status.get("status")
                
                if status == "completed":
                    output_filename = job_status.get("output_filename")
                    results.append(f"✅ {uploaded_file.name} → {output_filename}")
                    
                    # Store for download
                    if 'processed_files' not in st.session_state:
                        st.session_state.processed_files = []
                    st.session_state.processed_files.append({
                        'original_name': uploaded_file.name,
                        'output_filename': output_filename,
                        'job_id': job_id
                    })
                    break
                    
                elif status == "failed":
                    error = job_status.get("error", "Unknown error")
                    results.append(f"❌ {uploaded_file.name}: {error}")
                    break
                
                # Update progress
                elapsed = time.time() - start_time
                progress = min(elapsed / 120, 0.9)  # Estimate 2 minutes per video
                status_placeholder.info(f"⚙️ Processing {uploaded_file.name}... ({elapsed:.0f}s)")
                
                time.sleep(2)
            
            if time.time() - start_time >= max_wait_time:
                results.append(f"⏰ {uploaded_file.name}: Processing timeout")
            
            # Update overall progress
            progress_bar.progress((i + 1) / len(valid_files))
        
        # Show results
        status_placeholder.empty()
        st.header("Processing Results")
        
        for result in results:
            if result.startswith("✅"):
                st.success(result)
            else:
                st.error(result)
    
    # Download section
    if 'processed_files' in st.session_state and st.session_state.processed_files:
        st.header("📥 Download Processed Videos")
        
        for file_info in st.session_state.processed_files:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{file_info['original_name']}** → `{file_info['output_filename']}`")
            
            with col2:
                if st.button(f"📥 Download", key=f"download_{file_info['output_filename']}"):
                    # Download from backend
                    video_data = api.download_video(file_info['output_filename'])
                    
                    if video_data:
                        st.download_button(
                            label="💾 Save File",
                            data=video_data,
                            file_name=file_info['output_filename'],
                            mime="video/mp4",
                            key=f"save_{file_info['output_filename']}"
                        )
                    else:
                        st.error("Download failed")
        
        # Clear processed files
        if st.button("🗑️ Clear All Downloads"):
            st.session_state.processed_files = []
            st.rerun()
    
    # Footer info
    st.markdown("---")
    st.markdown("### 🏗️ **Architecture**")
    st.info("**Frontend**: Railway (Streamlit UI) → **Backend**: DigitalOcean (Heavy Processing)")

if __name__ == "__main__":
    main()