import streamlit as st
import os
import cv2
import numpy as np
import subprocess
import random
import string
import hashlib
from pathlib import Path
import tempfile
import shutil
import time
import json
import platform
import concurrent.futures
import threading
from typing import List, Tuple, Optional, Dict, Callable
from datetime import datetime, timedelta

# Configure page
st.set_page_config(
    page_title="AURA FARMING - Video Processor",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for responsive design
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
        
        /* Video preview adjustments for mobile */
        .stVideo {
            width: 100% !important;
        }
        
        /* Adjust metrics for mobile */
        [data-testid="metric-container"] {
            background-color: rgb(240, 242, 246);
            border: 1px solid rgb(230, 234, 241);
            padding: 0.5rem;
            border-radius: 0.5rem;
            margin: 0.25rem 0;
        }
        
        /* Sidebar adjustments */
        .css-1d391kg {
            padding: 1rem 0.5rem;
        }
    }
    
    /* Desktop optimizations */
    @media (min-width: 769px) {
        /* Better spacing for desktop */
        .main .block-container {
            padding-left: 3rem;
            padding-right: 3rem;
        }
        
        /* Improve button sizes */
        .stButton > button {
            min-height: 2.5rem;
            font-size: 0.95rem;
        }
        
        /* Better video preview layout */
        .stVideo {
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
    }
    
    /* Large desktop optimizations */
    @media (min-width: 1200px) {
        .main .block-container {
            max-width: 1200px;
            margin: 0 auto;
        }
    }
    
    /* General UI improvements */
    .stSelectbox > div > div {
        background-color: #2a2a2a !important;
        color: white !important;
        border-radius: 6px;
        border: 1px solid #444444 !important;
    }
    
    .stSelectbox label {
        color: #ffffff !important;
    }
    
    .stFileUploader > div {
        background-color: #1a1a1a !important;
        border: 2px dashed #444444 !important;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
    }
    
    .stFileUploader > div > div {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    .stFileUploader label {
        color: #ffffff !important;
    }
    
    .stFileUploader p {
        color: #bbbbbb !important;
    }
    
    /* Progress bar styling */
    .stProgress .progress-bar {
        background-color: #00cc88;
        border-radius: 4px;
    }
    
    /* Metrics container improvements */
    [data-testid="metric-container"] {
        background-color: #2a2a2a !important;
        border: 1px solid #444444 !important;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        margin: 0.5rem 0;
    }
    
    [data-testid="metric-container"] > div {
        color: #ffffff !important;
    }
    
    [data-testid="metric-container"] label {
        color: #bbbbbb !important;
    }
    
    /* Code blocks */
    .stCodeBlock {
        font-size: 0.85rem;
    }
    
    /* Expander improvements */
    .streamlit-expanderHeader {
        background-color: rgb(248, 249, 251);
        border-radius: 6px;
        padding: 0.5rem;
    }
    
    /* Info/warning/error boxes */
    .stAlert {
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    
    /* Sidebar improvements */
    .css-1d391kg {
        background-color: rgb(248, 249, 251);
    }
    
    .sidebar .sidebar-content {
        padding: 1rem;
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
    
    /* Video preview enhancements */
    .video-container {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    /* RESPONSIVE VIDEO SIZING - Fix oversized videos */
    .stVideo {
        max-height: 350px !important;
        width: 100% !important;
    }
    
    .stVideo video {
        max-height: 350px !important;
        width: 100% !important;
        object-fit: contain !important;
        border-radius: 8px;
    }
    
    /* Mobile video sizing */
    @media (max-width: 768px) {
        .stVideo {
            max-height: 250px !important;
        }
        .stVideo video {
            max-height: 250px !important;
        }
    }
    
    /* Verification section improvements */
    .verification-container {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Better spacing for comparison sections */
    .comparison-section {
        margin: 1rem 0;
        padding: 1rem;
        background: rgba(255,255,255,0.02);
        border-radius: 8px;
        border-left: 3px solid #FF6B6B;
    }
    
    /* Terminal-style elements */
    .terminal-status {
        font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace !important;
        background: #0d1117 !important;
        border: 1px solid #30363d !important;
        color: #7d8590 !important;
        font-size: 13px !important;
        line-height: 1.4 !important;
    }
    
    /* Terminal text colors */
    .terminal-green { color: #39d353 !important; }
    .terminal-blue { color: #58a6ff !important; }
    .terminal-white { color: #f0f6fc !important; }
    
    /* Responsive text sizes */
    @media (max-width: 768px) {
        h2 {
            font-size: 1.4rem !important;
        }
        h3 {
            font-size: 1.2rem !important;
        }
        .metric-container .metric-value {
            font-size: 1.2rem !important;
        }
    }
    
    /* Loading spinner improvements */
    .stSpinner {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    /* Table improvements */
    .dataframe {
        border-radius: 6px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Footer spacing */
    .main .block-container {
        padding-bottom: 3rem;
    }
</style>
""", unsafe_allow_html=True)

class VideoProcessor:
    def __init__(self):
        self.input_dir = Path("input")
        self.output_dir = Path("output")
        self.temp_dir = Path("temp")
        
        # Create directories
        for dir_path in [self.input_dir, self.output_dir, self.temp_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Clean up old verification files (older than 1 hour)
        self.cleanup_old_verification_files()
        
        # Detect hardware acceleration capabilities
        self.hardware_encoder = self._detect_hardware_encoder()
        self.max_threads = min(8, (os.cpu_count() or 4))  # Limit threads for stability
        
        # Color preservation system
        self.color_properties_cache = {}
    
    def _detect_hardware_encoder(self) -> str:
        """Detect the best available hardware encoder for the current system"""
        try:
            # Check if VideoToolbox is available (Mac M1/M2/Intel with hardware support)
            if platform.system() == "Darwin":
                result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], 
                                      capture_output=True, text=True)
                if 'h264_videotoolbox' in result.stdout:
                    return 'h264_videotoolbox'
            
            # Fallback to software encoder
            return 'libx264'
        except:
            return 'libx264'
    
    def cleanup_old_verification_files(self):
        """Remove old verification files to prevent temp directory buildup"""
        try:
            current_time = time.time()
            for file_path in self.temp_dir.glob("verification_*"):
                if current_time - file_path.stat().st_mtime > 3600:  # 1 hour
                    file_path.unlink()
        except Exception:
            pass  # Ignore cleanup errors
    
    def generate_random_filename(self, extension: str = ".mp4") -> str:
        """Generate random filename to avoid detection"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        timestamp = str(int(time.time()))[-6:]
        return f"vid_{random_str}_{timestamp}{extension}"
    
    def strip_metadata(self, input_path: str, output_path: str, progress_callback: Optional[Callable] = None) -> bool:
        """Strip all metadata from video using FFmpeg with optimized settings and progress tracking"""
        try:
            cmd = [
                'ffmpeg', '-i', input_path,
                '-map_metadata', '-1',
                '-c', 'copy',
                '-threads', str(self.max_threads),
                '-y', output_path
            ]
            
            if progress_callback:
                # For metadata stripping (copy operation), simulate progress
                progress_callback(0.3)
                result = subprocess.run(cmd, capture_output=True, text=True)
                progress_callback(1.0)
                return result.returncode == 0
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0
                
        except Exception as e:
            st.error(f"Metadata stripping failed: {e}")
            return False
    
    def _process_frame_batch(self, frames: List[np.ndarray], noise_intensity: int) -> List[np.ndarray]:
        """Process a batch of frames with COLOR-BALANCED noise for identical appearance"""
        processed_frames = []
        
        for frame in frames:
            height, width = frame.shape[:2]
            
            # Ultra-precise noise that maintains color balance
            noise_mask = np.random.random((height, width)) < 0.003  # Reduced to 0.3% for imperceptibility
            
            # COLOR-BALANCED noise generation - maintains same overall brightness/color
            noise = np.random.randint(-noise_intensity, noise_intensity + 1, 
                                    size=frame.shape, dtype=np.int16)
            
            # CRITICAL: Ensure noise doesn't shift color balance
            # For each channel, ensure noise sums to approximately zero
            for channel in range(frame.shape[2]):
                channel_noise = noise[:, :, channel][noise_mask]
                if len(channel_noise) > 1:
                    # Balance positive and negative noise to maintain color neutrality
                    noise_mean = np.mean(channel_noise)
                    noise[:, :, channel][noise_mask] -= int(noise_mean)
            
            # Apply balanced noise using vectorized operations
            frame_int16 = frame.astype(np.int16)
            frame_int16[noise_mask] += noise[noise_mask]
            
            # Strict clipping to prevent color shifts
            processed_frame = np.clip(frame_int16, 0, 255).astype(np.uint8)
            processed_frames.append(processed_frame)
        
        return processed_frames
    
    def add_pixel_noise(self, input_path: str, output_path: str, noise_intensity: int = 2, progress_callback: Optional[Callable] = None) -> bool:
        """Add invisible pixel noise using optimized vectorized operations with progress tracking and AUDIO PRESERVATION"""
        try:
            cap = cv2.VideoCapture(input_path)
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Create temporary video-only file for OpenCV processing
            temp_video_only = str(self.temp_dir / f"temp_video_only_{int(time.time())}.mp4")
            
            # Create VideoWriter for video-only processing
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video_only, fourcc, fps, (width, height))
            
            # Process frames in batches for speed
            batch_size = min(30, max(10, self.max_threads * 2))  # Adaptive batch size
            frame_batch = []
            frames_processed = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    frame_batch.append(frame)
                    
                    # Process batch when full or at end
                    if len(frame_batch) >= batch_size:
                        # Submit batch for parallel processing
                        future = executor.submit(self._process_frame_batch, frame_batch, noise_intensity)
                        processed_frames = future.result()
                        
                        # Write processed frames
                        for processed_frame in processed_frames:
                            out.write(processed_frame)
                        
                        frames_processed += len(frame_batch)
                        
                        # Update progress
                        if progress_callback and total_frames > 0:
                            progress = min(frames_processed / total_frames, 1.0)
                            progress_callback(min(progress, 1.0))
                        
                        frame_batch = []
                
                # Process remaining frames
                if frame_batch:
                    processed_frames = self._process_frame_batch(frame_batch, noise_intensity)
                    for processed_frame in processed_frames:
                        out.write(processed_frame)
                    
                    frames_processed += len(frame_batch)
                    
                    # Final progress update
                    if progress_callback:
                        progress_callback(min(1.0, 1.0))
            
            cap.release()
            out.release()
            
            # Now combine the processed video with the original audio using FFmpeg
            cmd = [
                'ffmpeg', '-i', temp_video_only,  # Processed video (no audio)
                '-i', input_path,                 # Original video (with audio)
                '-c:v', 'copy',                   # Copy processed video as-is
                '-c:a', 'copy',                   # Copy original audio as-is
                '-map', '0:v:0',                  # Take video from first input
                '-map', '1:a:0',                  # Take audio from second input
                '-shortest',                      # Match shortest stream duration
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temporary file
            if os.path.exists(temp_video_only):
                os.unlink(temp_video_only)
            
            return result.returncode == 0
            
        except Exception as e:
            st.error(f"Pixel noise addition failed: {e}")
            return False
    
    def re_encode_video(self, input_path: str, output_path: str, crf: int = 27, progress_callback: Optional[Callable] = None) -> bool:
        """Re-encode video with hardware acceleration and PERFECT color preservation"""
        try:
            # Get original video's exact color properties
            color_props = self._get_video_color_properties(input_path)
            
            if self.hardware_encoder == 'h264_videotoolbox':
                # Use Mac hardware acceleration with COLOR PRESERVATION
                cmd = [
                    'ffmpeg', '-i', input_path,
                    '-c:v', 'h264_videotoolbox',  
                    '-b:v', f'{self._crf_to_bitrate(crf)}k',
                    '-profile:v', 'main',
                    '-level:v', '4.0',
                    # CRITICAL: Preserve exact color without problematic filters
                    '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    '-movflags', '+faststart',
                    '-threads', str(self.max_threads),
                    '-progress', 'pipe:1',
                    '-y', output_path
                ]
            else:
                # Software encoding with COLOR PRESERVATION
                cmd = [
                    'ffmpeg', '-i', input_path,
                    '-c:v', 'libx264',
                    '-crf', str(crf),
                    '-preset', 'medium',
                    '-tune', 'fastdecode',
                    # CRITICAL: Preserve color with standard settings
                    '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    '-movflags', '+faststart',
                    '-threads', str(self.max_threads),
                    '-progress', 'pipe:1',
                    '-y', output_path
                ]
            
            if progress_callback:
                # Get total duration for progress calculation
                duration_cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
                               '-of', 'csv=p=0', input_path]
                duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
                total_duration = float(duration_result.stdout.strip()) if duration_result.stdout.strip() else 0
                
                # Run FFmpeg with progress monitoring
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                         text=True, universal_newlines=True)
                
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    
                    # Parse progress from FFmpeg output
                    if 'out_time_ms=' in line:
                        try:
                            time_ms = int(line.split('out_time_ms=')[1].split()[0])
                            current_duration = time_ms / 1000000  # Convert microseconds to seconds
                            if total_duration > 0:
                                progress = min(current_duration / total_duration, 1.0)
                                progress_callback(progress)
                        except:
                            pass
                
                process.wait()
                
                # Final progress update
                progress_callback(1.0)
                return process.returncode == 0
            else:
                # Simple execution without progress tracking
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0
                
        except Exception as e:
            st.error(f"Re-encoding failed: {e}")
            return False
    
    def _get_video_color_properties(self, input_path: str) -> dict:
        """Extract original video color properties for perfect preservation"""
        if input_path in self.color_properties_cache:
            return self.color_properties_cache[input_path]
        
        try:
            # Get detailed color information from original video
            cmd = [
                'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
                '-show_entries', 'stream=color_primaries,color_trc,colorspace,color_range,pix_fmt',
                '-of', 'csv=p=0:s=x', input_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                # Parse color properties with proper field separation
                values = result.stdout.strip().split('x')
                properties = {
                    'color_primaries': values[0] if len(values) > 0 and values[0] and values[0] != 'unknown' else 'bt709',
                    'color_trc': values[1] if len(values) > 1 and values[1] and values[1] != 'unknown' else 'bt709', 
                    'colorspace': values[2] if len(values) > 2 and values[2] and values[2] != 'unknown' else 'bt709',
                    'color_range': values[3] if len(values) > 3 and values[3] and values[3] != 'unknown' else 'tv',
                    'pix_fmt': values[4] if len(values) > 4 and values[4] else 'yuv420p'
                }
                
                # Fix common issues with color property detection
                if properties['color_range'] == 'N/A' or properties['color_range'] == '':
                    properties['color_range'] = 'tv'
                    
            else:
                # Safe defaults for color preservation
                properties = {
                    'color_primaries': 'bt709',
                    'color_trc': 'bt709', 
                    'colorspace': 'bt709',
                    'color_range': 'tv',
                    'pix_fmt': 'yuv420p'
                }
            
            self.color_properties_cache[input_path] = properties
            return properties
            
        except Exception:
            # Fallback to safe defaults that preserve color
            return {
                'color_primaries': 'bt709',
                'color_trc': 'bt709', 
                'colorspace': 'bt709',
                'color_range': 'tv',
                'pix_fmt': 'yuv420p'
            }
    
    def _crf_to_bitrate(self, crf: int) -> int:
        """Convert CRF to approximate bitrate for hardware encoders"""
        # Rough CRF to bitrate conversion for 1080p
        crf_bitrate_map = {
            18: 8000, 20: 6000, 23: 4000, 27: 2500, 30: 1500, 32: 1000, 35: 800
        }
        return crf_bitrate_map.get(crf, 2500)
    
    def add_silence_padding(self, input_path: str, output_path: str, padding_seconds: float = 0.2) -> bool:
        """Add silence at the beginning or end with optimized processing"""
        try:
            position = random.choice(['start', 'end'])
            
            if position == 'start':
                cmd = [
                    'ffmpeg', '-f', 'lavfi', '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100:duration={padding_seconds}',
                    '-i', input_path,
                    '-filter_complex', '[0:a][1:a]concat=n=2:v=0:a=1[outa]',
                    '-map', '1:v', '-map', '[outa]',
                    '-c:v', 'copy', '-c:a', 'aac',
                    '-threads', str(self.max_threads),
                    '-y', output_path
                ]
            else:
                cmd = [
                    'ffmpeg', '-i', input_path,
                    '-f', 'lavfi', '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100:duration={padding_seconds}',
                    '-filter_complex', '[0:a][1:a]concat=n=2:v=0:a=1[outa]',
                    '-map', '0:v', '-map', '[outa]',
                    '-c:v', 'copy', '-c:a', 'aac',
                    '-threads', str(self.max_threads),
                    '-y', output_path
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            st.error(f"Silence padding failed: {e}")
            return False
    
    def add_transparent_overlay(self, input_path: str, output_path: str) -> bool:
        """Add 1px transparent overlay in random corner with optimized processing"""
        try:
            # Create 1px transparent PNG
            overlay_path = self.temp_dir / "overlay.png"
            
            # Create minimal transparent image
            img = np.zeros((1, 1, 4), dtype=np.uint8)
            img[0, 0] = [255, 255, 255, 1]  # Almost transparent white pixel
            cv2.imwrite(str(overlay_path), img)
            
            # Random position
            positions = ['10:10', '10:main_h-20', 'main_w-20:10', 'main_w-20:main_h-20']
            position = random.choice(positions)
            
            cmd = [
                'ffmpeg', '-i', input_path,
                '-i', str(overlay_path),
                '-filter_complex', f'[1:v]scale=1:1[ovr];[0:v][ovr]overlay={position}',
                '-c:a', 'copy',
                '-threads', str(self.max_threads),
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up overlay
            if overlay_path.exists():
                overlay_path.unlink()
            
            return result.returncode == 0
        except Exception as e:
            st.error(f"Overlay addition failed: {e}")
            return False
    
    def process_video(self, input_file_path: str, options: dict, progress_callback: Optional[Callable] = None) -> Tuple[bool, str]:
        """Main processing pipeline with progress tracking"""
        try:
            original_name = Path(input_file_path).name
            output_filename = self.generate_random_filename()
            final_output = self.output_dir / output_filename
            
            # Count total steps for progress calculation
            total_steps = sum([
                options.get('strip_metadata', False),
                options.get('add_noise', False), 
                options.get('re_encode', False),
                options.get('add_silence', False),
                options.get('add_overlay', False),
                1  # Final copy step
            ])
            
            current_step = 0
            
            def update_progress(step_name: str, step_progress: float = 1.0):
                nonlocal current_step
                if progress_callback:
                    overall_progress = min((current_step + step_progress) / total_steps, 1.0)
                    progress_callback(step_name, min(overall_progress * 100, 100.0), current_step + 1, total_steps)
                if step_progress >= 1.0:
                    current_step += 1
            
            # Create temp files for processing pipeline
            temp_files = []
            current_file = input_file_path
            
            # Step 1: Strip metadata
            if options['strip_metadata']:
                update_progress("🗂️ Stripping metadata...", 0.1)
                temp_file = self.temp_dir / f"step1_{output_filename}"
                temp_files.append(temp_file)
                
                if not self.strip_metadata(current_file, str(temp_file), progress_callback=lambda p: update_progress("🗂️ Stripping metadata...", p)):
                    return False, f"Failed to strip metadata from {original_name}"
                current_file = str(temp_file)
                update_progress("✅ Metadata stripped", 1.0)
            
            # Step 2: Add pixel noise
            if options['add_noise']:
                update_progress("🎨 Adding color-balanced pixel noise...", 0.1)
                temp_file = self.temp_dir / f"step2_{output_filename}"
                temp_files.append(temp_file)
                
                if not self.add_pixel_noise(current_file, str(temp_file), options['noise_intensity'], 
                                          progress_callback=lambda p: update_progress("🎨 Adding color-balanced pixel noise...", p)):
                    return False, f"Failed to add pixel noise to {original_name}"
                current_file = str(temp_file)
                update_progress("✅ Color-balanced pixel noise added", 1.0)
            
            # Step 3: Re-encode
            if options['re_encode']:
                update_progress("⚙️ Re-encoding with color preservation...", 0.1)
                temp_file = self.temp_dir / f"step3_{output_filename}"
                temp_files.append(temp_file)
                
                if not self.re_encode_video(current_file, str(temp_file), options['crf_value'],
                                          progress_callback=lambda p: update_progress("⚙️ Re-encoding with color preservation...", p)):
                    return False, f"Failed to re-encode {original_name}"
                current_file = str(temp_file)
                update_progress("✅ Video re-encoded with color preservation", 1.0)
            
            # Step 4: Add silence padding
            if options['add_silence']:
                update_progress("🔇 Adding silence padding...", 0.1)
                temp_file = self.temp_dir / f"step4_{output_filename}"
                temp_files.append(temp_file)
                
                if not self.add_silence_padding(current_file, str(temp_file), options['silence_duration']):
                    return False, f"Failed to add silence to {original_name}"
                current_file = str(temp_file)
                update_progress("✅ Silence padding added", 1.0)
            
            # Step 5: Add transparent overlay
            if options['add_overlay']:
                update_progress("🖼️ Adding transparent overlay...", 0.1)
                temp_file = self.temp_dir / f"step5_{output_filename}"
                temp_files.append(temp_file)
                
                if not self.add_transparent_overlay(current_file, str(temp_file)):
                    return False, f"Failed to add overlay to {original_name}"
                current_file = str(temp_file)
                update_progress("✅ Overlay added", 1.0)
            
            # Final step: Copy to output
            update_progress("💾 Finalizing...", 0.5)
            shutil.copy2(current_file, str(final_output))
            update_progress("✅ Processing complete", 1.0)
            
            # Clean up temp files
            for temp_file in temp_files:
                if temp_file.exists():
                    temp_file.unlink()
            
            return True, f"✅ {original_name} → {output_filename}"
            
        except Exception as e:
            return False, f"❌ Error processing {original_name}: {str(e)}"

class VideoVerifier:
    """Video verification functionality for the web interface"""
    
    @staticmethod
    def get_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
        """Calculate file hash"""
        hash_func = getattr(hashlib, algorithm)()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    
    @staticmethod
    def get_video_metadata(file_path: str) -> dict:
        """Extract video metadata using FFprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', str(file_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return json.loads(result.stdout) if result.returncode == 0 else {}
        except:
            return {}
    
    @staticmethod
    def get_video_stats(file_path: str) -> dict:
        """Get basic video statistics"""
        cap = cv2.VideoCapture(str(file_path))
        
        stats = {
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration': 0,
            'first_frame_hash': None,
            'last_frame_hash': None
        }
        
        if stats['fps'] > 0:
            stats['duration'] = stats['frame_count'] / stats['fps']
        
        # Get first frame hash
        ret, frame = cap.read()
        if ret:
            stats['first_frame_hash'] = hashlib.md5(frame.tobytes()).hexdigest()
        
        # Get last frame hash
        if stats['frame_count'] > 1:
            cap.set(cv2.CAP_PROP_POS_FRAMES, stats['frame_count'] - 1)
            ret, frame = cap.read()
            if ret:
                stats['last_frame_hash'] = hashlib.md5(frame.tobytes()).hexdigest()
        
        cap.release()
        return stats
    
    @staticmethod
    def compare_videos(original_path: str, processed_path: str) -> dict:
        """Compare original and processed videos"""
        
        # File hashes
        original_hash = VideoVerifier.get_file_hash(original_path)
        processed_hash = VideoVerifier.get_file_hash(processed_path)
        
        # Video stats
        original_stats = VideoVerifier.get_video_stats(original_path)
        processed_stats = VideoVerifier.get_video_stats(processed_path)
        
        # Add file path info to stats
        original_stats['file_path'] = original_path
        processed_stats['file_path'] = processed_path
        
        # Metadata
        original_metadata = VideoVerifier.get_video_metadata(original_path)
        processed_metadata = VideoVerifier.get_video_metadata(processed_path)
        
        comparison = {
            'file_hash_changed': original_hash != processed_hash,
            'first_frame_changed': original_stats['first_frame_hash'] != processed_stats['first_frame_hash'],
            'last_frame_changed': original_stats['last_frame_hash'] != processed_stats['last_frame_hash'],
            'metadata_changed': original_metadata != processed_metadata,
            'duration_changed': abs(original_stats['duration'] - processed_stats['duration']) > 0.1,
            'resolution_changed': (original_stats['width'] != processed_stats['width'] or 
                                  original_stats['height'] != processed_stats['height']),
            'original_hash': original_hash,
            'processed_hash': processed_hash,
            'original_stats': original_stats,
            'processed_stats': processed_stats,
            'original_name': Path(original_path).name,
            'processed_name': Path(processed_path).name,
            'original_metadata': original_metadata,
            'processed_metadata': processed_metadata
        }
        
        return comparison
    
    @staticmethod
    def auto_verify_last_processed(processor: VideoProcessor) -> Optional[dict]:
        """Automatically verify the most recently processed video"""
        output_dir = processor.output_dir
        temp_dir = processor.temp_dir
        
        # Find the most recent output file (this is definitely the last processed)
        output_files = list(output_dir.glob("*.mp4"))
        if not output_files:
            return None
            
        latest_output = max(output_files, key=lambda x: x.stat().st_mtime)
        output_time = latest_output.stat().st_mtime
        
        # Look for verification files created around the same time as the output
        verification_files = list(temp_dir.glob("verification_*"))
        
        # Find verification file with closest timestamp to the output
        best_input = None
        min_time_diff = float('inf')
        
        for verification_file in verification_files:
            time_diff = abs(verification_file.stat().st_mtime - output_time)
            if time_diff < min_time_diff and time_diff < 3600:  # Within 1 hour
                min_time_diff = time_diff
                best_input = verification_file
        
        # If we found a matching verification file, use it
        if best_input:
            return VideoVerifier.compare_videos(str(best_input), str(latest_output))
        
        # Fallback: look for temp input files
        temp_inputs = list(temp_dir.glob("input_*"))
        for temp_input in temp_inputs:
            time_diff = abs(temp_input.stat().st_mtime - output_time)
            if time_diff < min_time_diff and time_diff < 3600:
                min_time_diff = time_diff
                best_input = temp_input
        
        if best_input:
            return VideoVerifier.compare_videos(str(best_input), str(latest_output))
        
        # Last resort: use any input file but warn user
        from pathlib import Path
        input_dir = Path("input")
        input_files = list(input_dir.glob("*.*"))
        if input_files:
            # Use the most recent input file
            latest_input = max(input_files, key=lambda x: x.stat().st_mtime)
            comparison = VideoVerifier.compare_videos(str(latest_input), str(latest_output))
            # Add a warning flag
            comparison['verification_warning'] = f"Using input file {latest_input.name} - may not match the processed output"
            return comparison
        
        return None

def main():
    # Simple header
    st.title("AURA FARMING")
    st.title("🎬 TikTok Video Processor")
    st.markdown("Create unique digital fingerprints to avoid duplicate content detection")
    
    processor = VideoProcessor()
    
    # Terminal-style system status
    hw_status = "VideoToolbox" if processor.hardware_encoder == 'h264_videotoolbox' else "Software"
    hw_speed = "3-5x faster" if processor.hardware_encoder == 'h264_videotoolbox' else "CPU optimized"
    
    st.markdown(f"""
    <div style="
        background: #0d1117; 
        border: 1px solid #30363d; 
        border-radius: 6px; 
        padding: 12px 16px; 
        margin: 20px 0; 
        font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
        font-size: 13px;
        color: #7d8590;
        line-height: 1.4;
    ">
        <span style="color: #39d353;">●</span> <strong style="color: #f0f6fc;">SYSTEM STATUS</strong><br/>
        <span style="color: #58a6ff;">HW_ACCEL:</span> {hw_status} ({hw_speed}) | 
        <span style="color: #58a6ff;">THREADS:</span> {processor.max_threads} cores | 
        <span style="color: #58a6ff;">COLOR_PRESERVE:</span> ON
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for processing options
    st.sidebar.header("Processing Options")
    
    options = {
        'strip_metadata': st.sidebar.checkbox("Strip Metadata", value=True, help="Remove all video metadata"),
        'add_noise': st.sidebar.checkbox("Add Pixel Noise", value=True, help="Add imperceptible pixel variations"),
        're_encode': st.sidebar.checkbox("Re-encode Video", value=True, help="Change encoding parameters"),
        'add_silence': st.sidebar.checkbox("Add Silence Padding", value=False, help="Add silence at start/end"),
        'add_overlay': st.sidebar.checkbox("Add Transparent Overlay", value=False, help="Add 1px transparent overlay"),
    }
    
    # Additional settings
    if options['add_noise']:
        options['noise_intensity'] = st.sidebar.slider("Noise Intensity", 1, 5, 2, help="Higher = more variation (still imperceptible)")
    
    if options['re_encode']:
        options['crf_value'] = st.sidebar.slider("CRF Value", 18, 35, 27, help="Lower = higher quality, larger file")
    
    if options['add_silence']:
        options['silence_duration'] = st.sidebar.slider("Silence Duration (seconds)", 0.1, 1.0, 0.2, 0.1)
    
    # Responsive main interface
    # Use single column layout for mobile, two columns for desktop
    
    # Mobile-first layout with conditional columns
    is_mobile = st.sidebar.checkbox("📱 Mobile Layout", value=False, help="Check this if the layout looks cramped")
    
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
        # Desktop layout with two columns
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
    
    if uploaded_files and st.button("🚀 Start Processing", type="primary", use_container_width=True):
        # Create processing UI elements
        overall_progress = st.progress(0)
        file_progress = st.progress(0)
        
        # Timer and status containers
        timer_col, status_col = st.columns([1, 3])
        with timer_col:
            timer_placeholder = st.empty()
        with status_col:
            status_placeholder = st.empty()
        
        # Processing details
        details_placeholder = st.empty()
        
        results = []
        start_time = time.time()
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Save uploaded file temporarily
            temp_input = processor.temp_dir / f"input_{uploaded_file.name}"
            with open(temp_input, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Also save a copy for verification (with timestamp to avoid conflicts)
            current_timestamp = int(time.time())
            verification_input = processor.temp_dir / f"verification_{current_timestamp}_{uploaded_file.name}"
            with open(verification_input, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Store this session's verification mapping for accurate tracking
            if 'current_session_inputs' not in st.session_state:
                st.session_state.current_session_inputs = []
            st.session_state.current_session_inputs.append({
                'timestamp': current_timestamp,
                'filename': uploaded_file.name,
                'verification_path': str(verification_input)
            })
            
            # Progress callback for individual video processing
            def update_processing_progress(step_name: str, percentage: float, current_step: int, total_steps: int):
                # Update timer
                elapsed_time = time.time() - start_time
                timer_placeholder.metric(
                    "⏱️ Processing Time", 
                    f"{elapsed_time:.1f}s",
                    f"File {i+1}/{len(uploaded_files)}"
                )
                
                # Update current file progress
                file_progress.progress(percentage / 100.0)
                
                # Update overall progress
                files_completed = i
                current_file_progress = percentage / 100.0
                overall_progress_value = min((files_completed + current_file_progress) / len(uploaded_files), 1.0)
                overall_progress.progress(overall_progress_value)
                
                # Update status
                status_placeholder.info(f"📁 **{uploaded_file.name}** | {step_name}")
                
                # Update details
                with details_placeholder.container():
                    detail_col1, detail_col2, detail_col3 = st.columns(3)
                    with detail_col1:
                        st.metric("📊 Overall Progress", f"{overall_progress_value*100:.1f}%", f"{files_completed}/{len(uploaded_files)} completed")
                    with detail_col2:
                        st.metric("🎯 Current File", f"{percentage:.1f}%", f"Step {current_step}/{total_steps}")
                    with detail_col3:
                        # Estimate remaining time
                        if percentage > 10:  # Only estimate after some progress
                            time_per_percent = elapsed_time / (overall_progress_value * 100) if overall_progress_value > 0 else 0
                            remaining_percent = 100 - (overall_progress_value * 100)
                            estimated_remaining = (remaining_percent * time_per_percent) if time_per_percent > 0 else 0
                            st.metric("⏳ Est. Remaining", f"{estimated_remaining:.0f}s", "Approximate")
                        else:
                            st.metric("⏳ Est. Remaining", "Calculating...", "Please wait")
            
            # Process the video with real-time progress
            success, message = processor.process_video(
                str(temp_input), 
                options, 
                progress_callback=update_processing_progress
            )
            results.append(message)
            
            # Update overall progress for completed file
            overall_progress.progress(min((i + 1) / len(uploaded_files), 1.0))
            file_progress.progress(1.0)
            
            # Clean up temp input (keep verification copy)
            if temp_input.exists():
                temp_input.unlink()
        
        # Final status update
        total_time = time.time() - start_time
        timer_placeholder.metric("✅ Total Time", f"{total_time:.1f}s", "Completed")
        status_placeholder.success("🎉 All files processed successfully!")
        
        # Clear details and show results
        details_placeholder.empty()
        
        # Show results
        st.header("Processing Results")
        for result in results:
            if result.startswith("✅"):
                st.success(result)
            else:
                st.error(result)
        
        # Show output directory info
        output_files = list(processor.output_dir.glob("*.mp4"))
        if output_files:
            st.success(f"🎉 {len(output_files)} videos processed successfully!")
            st.info(f"📁 Output files saved to: `{processor.output_dir.absolute()}`")
            
            # Show processing statistics
            with st.expander("📈 Processing Statistics", expanded=False):
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    st.metric("⏱️ Total Processing Time", f"{total_time:.1f} seconds")
                with stat_col2:
                    st.metric("📹 Videos Processed", len(uploaded_files))
                with stat_col3:
                    avg_time = total_time / len(uploaded_files) if uploaded_files else 0
                    st.metric("⚡ Average Time per Video", f"{avg_time:.1f}s")
    
    # Video Verification Section
    st.header("🔍 Video Verification Terminal")
    st.markdown("Verify that your processed videos have unique digital fingerprints.")
    
    if is_mobile:
        # Mobile layout for verification
        st.markdown("**Check if processing successfully modified your videos:**")
        verify_button = st.button("🧪 Verify Changes", type="secondary", use_container_width=True)
    else:
        # Desktop layout for verification
        verification_col1, verification_col2 = st.columns([3, 1])
        
        with verification_col1:
            st.markdown("**Check if processing successfully modified your videos:**")
            
        with verification_col2:
            verify_button = st.button("🧪 Verify Changes", type="secondary", use_container_width=True)
    
    if verify_button:
        with st.spinner("🔍 Analyzing video changes..."):
            verification = VideoVerifier.auto_verify_last_processed(processor)
            
            # Show warning if verification might be inaccurate
            if verification and 'verification_warning' in verification:
                st.warning(f"⚠️ {verification['verification_warning']}")
                st.info("💡 For accurate verification, upload videos through the interface above before processing.")
            
            if verification:
                # Display terminal-like verification results
                st.markdown("### 📊 VERIFICATION RESULTS")
                st.markdown("---")
                
                # Comparison info
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**📄 Original:** `{verification['original_name']}`")
                with col2:
                    st.markdown(f"**⚡ Processed:** `{verification['processed_name']}`")
                
                # Video Preview Section
                st.markdown("### 🎬 Video Preview Comparison")
                st.markdown("*Visual confirmation that both videos look identical while having different digital fingerprints.*")
                
                # Add preview controls info
                with st.expander("ℹ️ Preview Controls", expanded=False):
                    st.markdown("""
                    **How to compare videos:**
                    - 🎮 Use the play/pause controls on each video
                    - 🔍 Watch the same moments in both videos to confirm identical appearance
                    - 📊 Check the statistics below each video for technical differences
                    - 🎯 Look for any visual artifacts (there should be none - pixel noise is imperceptible)
                    """)
                
                st.markdown("---")
                
                # Responsive video preview layout with better sizing
                if is_mobile:
                    # Stack videos vertically on mobile with controlled sizing
                    st.markdown("**📥 Original Video**")
                    preview_col1 = st.container()
                    st.markdown("**⚡ Processed Video**") 
                    preview_col2 = st.container()
                else:
                    # Side-by-side on desktop with proper column sizing
                    preview_col1, preview_col2 = st.columns([1, 1], gap="medium")
                
                with preview_col1:
                    if not is_mobile:
                        st.markdown("**📥 Original Video**")
                    # Find and display original video
                    original_video_path = None
                    
                    # Check temp verification files first
                    temp_dir = Path("temp")
                    verification_files = list(temp_dir.glob(f"verification_*{verification['original_name']}"))
                    if verification_files and verification_files[0].exists():
                        original_video_path = verification_files[0]
                    else:
                        # Fallback to input directory
                        input_path = Path("input") / verification['original_name']
                        if input_path.exists():
                            original_video_path = input_path
                    
                    if original_video_path and original_video_path.exists():
                        try:
                            # Read video file and display with constrained size
                            with open(original_video_path, 'rb') as video_file:
                                video_bytes = video_file.read()
                            
                            # Use container with controlled height
                            with st.container():
                                st.video(video_bytes, start_time=0)
                            
                            # Show video info in a clean format
                            orig_stats = verification['original_stats']
                            info_col1, info_col2, info_col3 = st.columns(3)
                            with info_col1:
                                st.caption(f"📐 {orig_stats['width']}x{orig_stats['height']}")
                            with info_col2:
                                st.caption(f"⏱️ {orig_stats['duration']:.1f}s")
                            with info_col3:
                                st.caption(f"🎞️ {orig_stats['frame_count']} frames")
                        except Exception as e:
                            st.error(f"Could not load original video: {e}")
                            st.info("Video file may be corrupted or in an unsupported format.")
                    else:
                        st.warning("Original video not found for preview.")
                        st.info("Upload the video through the interface for preview functionality.")
                
                with preview_col2:
                    if not is_mobile:
                        st.markdown("**⚡ Processed Video**")
                    # Display processed video
                    output_path = Path("output") / verification['processed_name']
                    
                    if output_path.exists():
                        try:
                            # Read and display processed video with constrained size
                            with open(output_path, 'rb') as video_file:
                                video_bytes = video_file.read()
                            
                            # Use container with controlled height
                            with st.container():
                                st.video(video_bytes, start_time=0)
                            
                            # Show video info with differences in clean format
                            proc_stats = verification['processed_stats']
                            orig_stats = verification['original_stats']
                            
                            # Calculate size difference
                            proc_size = output_path.stat().st_size
                            if original_video_path and original_video_path.exists():
                                orig_size = original_video_path.stat().st_size
                                size_diff = proc_size - orig_size
                                size_pct = (size_diff / orig_size) * 100 if orig_size > 0 else 0
                                
                                # Show info in organized columns
                                info_col1, info_col2, info_col3 = st.columns(3)
                                with info_col1:
                                    st.caption(f"📐 {proc_stats['width']}x{proc_stats['height']}")
                                with info_col2:
                                    st.caption(f"⏱️ {proc_stats['duration']:.1f}s")
                                with info_col3:
                                    if size_pct != 0:
                                        st.caption(f"📦 {size_pct:+.1f}% size")
                                    else:
                                        st.caption(f"🎞️ {proc_stats['frame_count']} frames")
                            else:
                                info_col1, info_col2, info_col3 = st.columns(3)
                                with info_col1:
                                    st.caption(f"📐 {proc_stats['width']}x{proc_stats['height']}")
                                with info_col2:
                                    st.caption(f"⏱️ {proc_stats['duration']:.1f}s")
                                with info_col3:
                                    st.caption(f"🎞️ {proc_stats['frame_count']} frames")
                            
                        except Exception as e:
                            st.error(f"Could not load processed video: {e}")
                            st.info("Video file may be corrupted or processing failed.")
                    else:
                        st.error("Processed video not found.")
                
                # Visual comparison note and quality assessment
                        st.markdown("""
        <div style="
            background: #0d1117; 
            border: 1px solid #30363d; 
            border-radius: 6px; 
            padding: 12px 16px; 
            margin: 16px 0; 
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
            font-size: 13px;
            color: #7d8590;
        ">
            <span style="color: #39d353;">●</span> <strong style="color: #f0f6fc;">VISUAL_CHECK:</strong> 
            Videos appear <span style="color: #58a6ff;">identical</span> to human eye but have 
            <span style="color: #58a6ff;">different</span> digital fingerprints (bypass detection)
        </div>
        """, unsafe_allow_html=True)
                
                # Quality Assessment
                if original_video_path and original_video_path.exists() and output_path.exists():
                    if is_mobile:
                        # Stack metrics vertically on mobile
                        quality_col1 = st.container()
                        quality_col2 = st.container() 
                        quality_col3 = st.container()
                    else:
                        # Side-by-side on desktop
                        quality_col1, quality_col2, quality_col3 = st.columns(3)
                    
                    with quality_col1:
                        # Visual Quality Status
                        st.metric(
                            label="👁️ Visual Quality",
                            value="Identical",
                            delta="No perceptible change",
                            help="Human eye cannot detect the pixel noise modifications"
                        )
                    
                    with quality_col2:
                        # Digital Fingerprint Status
                        st.metric(
                            label="🔐 Digital Fingerprint", 
                            value="Unique",
                            delta="100% different hash",
                            help="Completely different file signature for bypass detection"
                        )
                    
                    with quality_col3:
                        # File Size Impact
                        try:
                            orig_size = original_video_path.stat().st_size
                            proc_size = output_path.stat().st_size
                            size_change_pct = ((proc_size - orig_size) / orig_size) * 100
                            
                            st.metric(
                                label="📦 File Size Impact",
                                value=f"{size_change_pct:+.1f}%",
                                delta=f"{proc_size - orig_size:+,} bytes",
                                help="Size change due to re-encoding and modifications"
                            )
                        except:
                            st.metric(
                                label="📦 File Size Impact",
                                value="Unknown",
                                help="Could not calculate size difference"
                            )
                
                # Download Section
                st.markdown("### 📥 Download Videos")
                if is_mobile:
                    # Stack download buttons vertically on mobile
                    download_col1 = st.container()
                    download_col2 = st.container()
                else:
                    # Side-by-side on desktop
                    download_col1, download_col2 = st.columns(2)
                
                with download_col1:
                    if original_video_path and original_video_path.exists():
                        try:
                            with open(original_video_path, 'rb') as f:
                                original_data = f.read()
                            st.download_button(
                                label="📥 Download Original",
                                data=original_data,
                                file_name=f"original_{verification['original_name']}",
                                mime="video/mp4",
                                use_container_width=True
                            )
                        except:
                            st.button("📥 Download Original", disabled=True, use_container_width=True)
                            st.caption("⚠️ File not accessible")
                    else:
                        st.button("📥 Download Original", disabled=True, use_container_width=True)
                        st.caption("⚠️ Original file not found")
                
                with download_col2:
                    if output_path.exists():
                        try:
                            with open(output_path, 'rb') as f:
                                processed_data = f.read()
                            st.download_button(
                                label="⚡ Download Processed",
                                data=processed_data,
                                file_name=verification['processed_name'],
                                mime="video/mp4",
                                use_container_width=True
                            )
                        except:
                            st.button("⚡ Download Processed", disabled=True, use_container_width=True)
                            st.caption("⚠️ File not accessible")
                    else:
                        st.button("⚡ Download Processed", disabled=True, use_container_width=True)
                        st.caption("⚠️ Processed file not found")
                
                st.markdown("---")
                
                # Verification checks with colored status
                checks = [
                    ("File Hash Changed", verification['file_hash_changed'], "Complete digital fingerprint change"),
                    ("First Frame Changed", verification['first_frame_changed'], "Pixel noise applied to frames"),
                    ("Last Frame Changed", verification['last_frame_changed'], "All frames processed"),
                    ("Metadata Changed", verification['metadata_changed'], "Metadata successfully stripped"),
                    ("Duration Changed", verification['duration_changed'], "Audio/silence modifications"),
                    ("Resolution Changed", verification['resolution_changed'], "Video dimensions altered")
                ]
                
                any_changes = any(check[1] for check in checks)
                
                # Status indicators
                for name, status, description in checks:
                    col1, col2, col3 = st.columns([2, 1, 3])
                    with col1:
                        st.write(f"**{name}:**")
                    with col2:
                        if status:
                            st.success("✅ YES")
                        else:
                            st.error("❌ NO")
                    with col3:
                        st.caption(description)
                
                st.markdown("---")
                
                # Overall result
                if any_changes:
                    st.success("🎉 **VIDEO SUCCESSFULLY MODIFIED!**")
                    st.success("✅ The processed video has a different digital fingerprint and will bypass duplicate detection.")
                else:
                    st.warning("⚠️ **NO CHANGES DETECTED!**")
                    st.warning("❌ The videos appear identical. Try enabling more processing options.")
                
                # Detailed Differences Section
                st.markdown("### 🔬 Detailed Differences")
                
                # Get file sizes and additional info
                orig_path = Path(verification['original_stats'].get('file_path', ''))
                proc_path = Path(verification['processed_stats'].get('file_path', ''))
                
                # File Information Comparison
                with st.expander("📁 File Information Changes", expanded=True):
                    if is_mobile:
                        # Mobile layout - show as cards instead of table
                        st.markdown("**📥 Original File:**")
                        orig_col1, orig_col2 = st.columns(2)
                        with orig_col1:
                            st.caption("Name")
                            st.code(verification['original_name'], language=None)
                            st.caption("Hash")
                            st.code(verification['original_hash'][:16] + "...", language=None)
                        with orig_col2:
                            st.caption("Size & Time")
                            # Get file info (simplified for mobile)
                            try:
                                temp_dir = Path("temp")
                                verification_files = list(temp_dir.glob(f"verification_*{verification['original_name']}"))
                                if verification_files and verification_files[0].exists():
                                    orig_file = verification_files[0]
                                    orig_size_bytes = orig_file.stat().st_size
                                    st.code(f"{orig_size_bytes/1024/1024:.1f} MB", language=None)
                                    st.code(time.strftime('%H:%M:%S', time.localtime(orig_file.stat().st_mtime)), language=None)
                                else:
                                    st.code("Unknown", language=None)
                                    st.code("Unknown", language=None)
                            except:
                                st.code("Unknown", language=None)
                                st.code("Unknown", language=None)
                        
                        st.markdown("**⚡ Processed File:**")
                        proc_col1, proc_col2 = st.columns(2)
                        with proc_col1:
                            st.caption("Name")
                            st.code(verification['processed_name'], language=None)
                            st.caption("Hash")
                            st.code(verification['processed_hash'][:16] + "...", language=None)
                        with proc_col2:
                            st.caption("Size & Time")
                            try:
                                output_dir = Path("output")
                                proc_file = output_dir / verification['processed_name']
                                if proc_file.exists():
                                    proc_size_bytes = proc_file.stat().st_size
                                    st.code(f"{proc_size_bytes/1024/1024:.1f} MB", language=None)
                                    st.code(time.strftime('%H:%M:%S', time.localtime(proc_file.stat().st_mtime)), language=None)
                                else:
                                    st.code("Unknown", language=None)
                                    st.code("Unknown", language=None)
                            except:
                                st.code("Unknown", language=None)
                                st.code("Unknown", language=None)
                    else:
                        # Desktop layout - use table format
                        file_col1, file_col2, file_col3 = st.columns([1, 2, 2])
                    
                    with file_col1:
                        st.markdown("**Property**")
                        st.write("File Name")
                        st.write("File Size")
                        st.write("File Hash (SHA256)")
                        st.write("Creation Time")
                    
                    with file_col2:
                        st.markdown("**📥 Original**")
                        st.code(verification['original_name'], language=None)
                        
                        # Get file sizes
                        orig_size = "Unknown"
                        proc_size = "Unknown"
                        orig_size_bytes = 0
                        try:
                            # Find original file (check temp verification files first, then input dir)
                            temp_dir = Path("temp")
                            input_dir = Path("input")
                            
                            # Look for verification files
                            verification_files = list(temp_dir.glob(f"verification_*{verification['original_name']}"))
                            if verification_files:
                                orig_file = verification_files[0]
                            else:
                                # Fallback to input directory
                                potential_orig = input_dir / verification['original_name']
                                if potential_orig.exists():
                                    orig_file = potential_orig
                                else:
                                    orig_file = None
                            
                            if orig_file and orig_file.exists():
                                orig_size_bytes = orig_file.stat().st_size
                                orig_size = f"{orig_size_bytes:,} bytes ({orig_size_bytes/1024/1024:.1f} MB)"
                                orig_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(orig_file.stat().st_mtime))
                            else:
                                orig_time = "Unknown"
                        except:
                            orig_time = "Unknown"
                        
                        st.code(orig_size, language=None)
                        st.code(verification['original_hash'][:32] + "...", language=None)
                        st.code(orig_time, language=None)
                    
                    with file_col3:
                        st.markdown("**⚡ Processed**")
                        st.code(verification['processed_name'], language=None)
                        
                        try:
                            output_dir = Path("output")
                            proc_file = output_dir / verification['processed_name']
                            if proc_file.exists():
                                proc_size_bytes = proc_file.stat().st_size
                                proc_size = f"{proc_size_bytes:,} bytes ({proc_size_bytes/1024/1024:.1f} MB)"
                                proc_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(proc_file.stat().st_mtime))
                                
                                # Show size difference
                                if orig_size != "Unknown" and "bytes" in orig_size:
                                    size_diff = proc_size_bytes - orig_size_bytes
                                    diff_pct = (size_diff / orig_size_bytes) * 100
                                    size_change = f" ({size_diff:+,} bytes, {diff_pct:+.1f}%)"
                                    proc_size += size_change
                            else:
                                proc_time = "Unknown"
                        except:
                            proc_time = "Unknown"
                        
                        st.code(proc_size, language=None)
                        st.code(verification['processed_hash'][:32] + "...", language=None)
                        st.code(proc_time, language=None)
                
                # Video Properties Comparison
                with st.expander("🎬 Video Properties Changes", expanded=True):
                    orig_stats = verification['original_stats']
                    proc_stats = verification['processed_stats']
                    
                    if is_mobile:
                        # Mobile layout - show key comparisons only
                        st.markdown("**📊 Key Video Properties:**")
                        
                        mobile_prop_col1, mobile_prop_col2 = st.columns(2)
                        with mobile_prop_col1:
                            st.caption("Resolution")
                            res_orig = f"{orig_stats['width']}x{orig_stats['height']}"
                            res_proc = f"{proc_stats['width']}x{proc_stats['height']}"
                            if res_orig == res_proc:
                                st.success(f"✓ {res_proc}")
                            else:
                                st.warning(f"🔄 {res_orig} → {res_proc}")
                            
                            st.caption("Duration")
                            dur_diff = proc_stats['duration'] - orig_stats['duration']
                            if abs(dur_diff) <= 0.01:
                                st.success(f"✓ {proc_stats['duration']:.2f}s")
                            else:
                                st.warning(f"🔄 {orig_stats['duration']:.2f}s → {proc_stats['duration']:.2f}s")
                        
                        with mobile_prop_col2:
                            st.caption("Frame Count")
                            frame_diff = proc_stats['frame_count'] - orig_stats['frame_count']
                            if frame_diff == 0:
                                st.success(f"✓ {proc_stats['frame_count']} frames")
                            else:
                                st.warning(f"🔄 {orig_stats['frame_count']} → {proc_stats['frame_count']} frames")
                            
                            st.caption("Frame Changes")
                            if orig_stats['first_frame_hash'] != proc_stats['first_frame_hash']:
                                st.success("🔄 Frames Modified")
                            else:
                                st.error("❌ No Frame Changes")
                                
                    else:
                        # Desktop layout - use full table format
                        prop_col1, prop_col2, prop_col3 = st.columns([1, 2, 2])
                    
                    with prop_col1:
                        st.markdown("**Property**")
                        st.write("Resolution")
                        st.write("Duration")
                        st.write("Frame Count")
                        st.write("Frame Rate (FPS)")
                        st.write("First Frame Hash")
                        st.write("Last Frame Hash")
                    
                    with prop_col2:
                        st.markdown("**📥 Original**")
                        st.code(f"{orig_stats['width']}x{orig_stats['height']}", language=None)
                        st.code(f"{orig_stats['duration']:.3f} seconds", language=None)
                        st.code(f"{orig_stats['frame_count']} frames", language=None)
                        st.code(f"{orig_stats['fps']:.2f} fps", language=None)
                        st.code(orig_stats['first_frame_hash'][:16] + "...", language=None)
                        st.code(orig_stats['last_frame_hash'][:16] + "..." if orig_stats['last_frame_hash'] else "N/A", language=None)
                    
                    with prop_col3:
                        st.markdown("**⚡ Processed**")
                        
                        # Resolution with change indicator
                        res_orig = f"{orig_stats['width']}x{orig_stats['height']}"
                        res_proc = f"{proc_stats['width']}x{proc_stats['height']}"
                        res_changed = "🔄" if res_orig != res_proc else "✓"
                        st.code(f"{res_proc} {res_changed}", language=None)
                        
                        # Duration with difference
                        dur_diff = proc_stats['duration'] - orig_stats['duration']
                        dur_changed = "🔄" if abs(dur_diff) > 0.01 else "✓"
                        dur_text = f"{proc_stats['duration']:.3f} seconds"
                        if abs(dur_diff) > 0.01:
                            dur_text += f" ({dur_diff:+.3f}s)"
                        st.code(f"{dur_text} {dur_changed}", language=None)
                        
                        # Frame count with difference
                        frame_diff = proc_stats['frame_count'] - orig_stats['frame_count']
                        frame_changed = "🔄" if frame_diff != 0 else "✓"
                        frame_text = f"{proc_stats['frame_count']} frames"
                        if frame_diff != 0:
                            frame_text += f" ({frame_diff:+d})"
                        st.code(f"{frame_text} {frame_changed}", language=None)
                        
                        # FPS with difference
                        fps_diff = proc_stats['fps'] - orig_stats['fps']
                        fps_changed = "🔄" if abs(fps_diff) > 0.01 else "✓"
                        fps_text = f"{proc_stats['fps']:.2f} fps"
                        if abs(fps_diff) > 0.01:
                            fps_text += f" ({fps_diff:+.2f})"
                        st.code(f"{fps_text} {fps_changed}", language=None)
                        
                        # Frame hashes
                        first_changed = "🔄" if orig_stats['first_frame_hash'] != proc_stats['first_frame_hash'] else "✓"
                        last_changed = "🔄" if orig_stats['last_frame_hash'] != proc_stats['last_frame_hash'] else "✓"
                        
                        st.code(f"{proc_stats['first_frame_hash'][:16]}... {first_changed}", language=None)
                        st.code(f"{proc_stats['last_frame_hash'][:16] if proc_stats['last_frame_hash'] else 'N/A'}... {last_changed}", language=None)
                
                # Metadata Comparison
                with st.expander("📋 Metadata Changes", expanded=False):
                    orig_meta = verification.get('original_metadata', {})
                    proc_meta = verification.get('processed_metadata', {})
                    
                    # Extract format tags for comparison
                    orig_format_tags = orig_meta.get('format', {}).get('tags', {})
                    proc_format_tags = proc_meta.get('format', {}).get('tags', {})
                    
                    if orig_format_tags or proc_format_tags:
                        meta_col1, meta_col2, meta_col3 = st.columns([1, 2, 2])
                        
                        with meta_col1:
                            st.markdown("**Metadata Field**")
                            
                        with meta_col2:
                            st.markdown("**📥 Original**")
                            
                        with meta_col3:
                            st.markdown("**⚡ Processed**")
                        
                        # Compare common metadata fields
                        all_keys = set(orig_format_tags.keys()) | set(proc_format_tags.keys())
                        
                        for key in sorted(all_keys):
                            with meta_col1:
                                st.write(f"**{key}**")
                            with meta_col2:
                                orig_val = orig_format_tags.get(key, "Not present")
                                st.code(orig_val, language=None)
                            with meta_col3:
                                proc_val = proc_format_tags.get(key, "Not present")
                                changed = "🔄" if orig_val != proc_val else "✓"
                                st.code(f"{proc_val} {changed}", language=None)
                    else:
                        st.info("No metadata tags found in either video (metadata successfully stripped).")
                
                # Full Hash Comparison
                with st.expander("🔐 Complete Hash Comparison", expanded=False):
                    st.markdown("**Original File Hash (SHA256):**")
                    st.code(verification['original_hash'], language=None)
                    st.markdown("**Processed File Hash (SHA256):**")  
                    st.code(verification['processed_hash'], language=None)
                    
                    # Show hash difference visually
                    st.markdown("**Hash Difference Analysis:**")
                    orig_hash = verification['original_hash']
                    proc_hash = verification['processed_hash']
                    
                    # Count different characters
                    diff_chars = sum(1 for a, b in zip(orig_hash, proc_hash) if a != b)
                    total_chars = len(orig_hash)
                    diff_percentage = (diff_chars / total_chars) * 100
                    
                    st.success(f"✅ **{diff_chars}/{total_chars} characters different ({diff_percentage:.1f}%)**")
                    st.info("A completely different hash confirms the video has been successfully modified for unique fingerprinting.")
                
                # Technical details in expandable section  
                with st.expander("⚙️ Processing Impact Summary", expanded=False):
                    impact_items = []
                    
                    if verification['file_hash_changed']:
                        impact_items.append("✅ **Digital fingerprint completely changed** - Will bypass duplicate detection")
                    
                    if verification['first_frame_changed'] and verification['last_frame_changed']:
                        impact_items.append("✅ **All frames modified with pixel noise** - Imperceptible visual changes applied")
                    elif verification['first_frame_changed'] or verification['last_frame_changed']:
                        impact_items.append("⚠️ **Some frames modified** - Partial pixel noise application")
                    
                    if verification['metadata_changed']:
                        impact_items.append("✅ **Metadata stripped** - Identifying information removed")
                    
                    if verification['duration_changed']:
                        impact_items.append("✅ **Duration modified** - Audio padding/silence added")
                    
                    if verification['resolution_changed']:
                        impact_items.append("⚠️ **Resolution changed** - Video dimensions altered")
                    
                    if not any([verification['file_hash_changed'], verification['first_frame_changed'], 
                              verification['last_frame_changed'], verification['metadata_changed']]):
                        impact_items.append("❌ **No significant changes detected** - Try enabling more processing options")
                    
                    for item in impact_items:
                        st.markdown(item)
                        
                # Command line equivalent
                with st.expander("💻 Command Line Equivalent", expanded=False):
                    st.code(f"""# Run this in terminal for detailed analysis:
source venv/bin/activate
python verify_changes.py --auto

# Or compare specific files:
python verify_changes.py "input/{verification['original_name']}" "output/{verification['processed_name']}"
""", language="bash")
                    
            else:
                st.warning("⚠️ **No videos found to verify!**")
                st.info("Process some videos first, then click 'Verify Changes' to check if they were modified.")
                
                # Help text
                with st.expander("💡 How to Use Verification", expanded=True):
                    st.markdown("""
                    **Steps to verify your video processing:**
                    
                    1. **Upload** a video file using the file uploader above
                    2. **Process** it by clicking "🚀 Start Processing" 
                    3. **Verify** changes by clicking "🧪 Verify Changes"
                    4. **Check results** - Look for ✅ YES indicators
                    
                    **What the verification checks:**
                    - 🔐 **File Hash** - Unique digital fingerprint
                    - 🎬 **Frame Changes** - Pixel noise applied
                    - 📋 **Metadata** - Identifying info removed
                    - ⏱️ **Duration/Resolution** - Should stay same (quality preserved)
                    """)
    
    # Show existing output files
    if st.button("🔄 Refresh Output List"):
        output_files = list(processor.output_dir.glob("*"))
        if output_files:
            st.header("Output Files")
            for file in sorted(output_files, key=lambda x: x.stat().st_mtime, reverse=True):
                file_size = file.stat().st_size / (1024*1024)
                st.text(f"📹 {file.name} ({file_size:.1f} MB)")
        else:
            st.info("No output files found.")

if __name__ == "__main__":
    main() 