#!/usr/bin/env python3
"""
DigitalOcean Backend API for Video Processing
FastAPI server that handles heavy video processing tasks
"""
import os
import cv2
import numpy as np
import subprocess
import random
import string
import hashlib
import time
import tempfile
import shutil
import json
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Callable
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import video processing classes from original app
import sys
sys.path.append('.')

# Set platform environment for optimizations
os.environ["PLATFORM"] = "digitalocean"
os.environ["DIGITALOCEAN"] = "true"

class VideoProcessor:
    """Video processing class optimized for DigitalOcean backend"""
    
    def __init__(self):
        self.input_dir = Path("api_input")
        self.output_dir = Path("api_output") 
        self.temp_dir = Path("api_temp")
        
        # Create directories
        for dir_path in [self.input_dir, self.output_dir, self.temp_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Clean up old files
        self.cleanup_old_files()
        
        # DigitalOcean optimized settings
        self.hardware_encoder = self._detect_hardware_encoder()
        self.max_threads = min(6, (os.cpu_count() or 4))  # DigitalOcean optimized
        self.color_properties_cache = {}
    
    def cleanup_old_files(self):
        """Clean up files older than 2 hours"""
        try:
            current_time = time.time()
            for directory in [self.input_dir, self.output_dir, self.temp_dir]:
                for file_path in directory.glob("*"):
                    if file_path.is_file() and current_time - file_path.stat().st_mtime > 7200:  # 2 hours
                        file_path.unlink()
        except Exception:
            pass
    
    def _detect_hardware_encoder(self) -> str:
        """Detect the best available hardware encoder"""
        try:
            result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], 
                                  capture_output=True, text=True)
            if 'h264_videotoolbox' in result.stdout:
                return 'h264_videotoolbox'
            return 'libx264'
        except:
            return 'libx264'
    
    def generate_random_filename(self, extension: str = ".mp4") -> str:
        """Generate random filename"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        timestamp = str(int(time.time()))[-6:]
        return f"processed_{random_str}_{timestamp}{extension}"
    
    def strip_metadata(self, input_path: str, output_path: str) -> bool:
        """Strip metadata from video"""
        try:
            cmd = [
                'ffmpeg', '-i', input_path,
                '-map_metadata', '-1',
                '-c', 'copy',
                '-threads', str(self.max_threads),
                '-y', output_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0
        except Exception:
            return False
    
    def add_pixel_noise(self, input_path: str, output_path: str, noise_intensity: int = 2) -> bool:
        """Add invisible pixel noise - DigitalOcean optimized"""
        try:
            cap = cv2.VideoCapture(input_path)
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # DigitalOcean memory check (more generous)
            estimated_memory_mb = (width * height * 3 * 30) / (1024 * 1024)
            if estimated_memory_mb > 1500:  # 1.5GB limit for DigitalOcean
                # Fallback: just copy file
                import shutil
                shutil.copy2(input_path, output_path)
                return True
            
            # Create temporary video file
            temp_video_only = str(self.temp_dir / f"temp_video_{int(time.time())}.mp4")
            
            # Process video
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video_only, fourcc, fps, (width, height))
            
            if not out.isOpened():
                return False
            
            # Process frames in batches
            batch_size = 15  # Optimized for DigitalOcean
            frame_batch = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_batch.append(frame)
                
                if len(frame_batch) >= batch_size:
                    # Process batch
                    processed_frames = self._process_frame_batch(frame_batch, noise_intensity)
                    for processed_frame in processed_frames:
                        out.write(processed_frame)
                    frame_batch.clear()
            
            # Process remaining frames
            if frame_batch:
                processed_frames = self._process_frame_batch(frame_batch, noise_intensity)
                for processed_frame in processed_frames:
                    out.write(processed_frame)
            
            cap.release()
            out.release()
            
            # Combine with original audio
            cmd = [
                'ffmpeg', '-i', temp_video_only,
                '-i', input_path,
                '-c:v', 'copy', '-c:a', 'copy',
                '-map', '0:v:0', '-map', '1:a:0',
                '-shortest', '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            # Cleanup
            if os.path.exists(temp_video_only):
                os.unlink(temp_video_only)
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _process_frame_batch(self, frames: List[np.ndarray], noise_intensity: int) -> List[np.ndarray]:
        """Process frame batch with pixel noise"""
        processed_frames = []
        
        for frame in frames:
            height, width = frame.shape[:2]
            
            # Create noise mask
            noise_mask = np.random.random((height, width)) < 0.003
            
            # Generate balanced noise
            noise = np.random.randint(-noise_intensity, noise_intensity + 1, 
                                    size=frame.shape, dtype=np.int16)
            
            # Apply noise
            frame_int16 = frame.astype(np.int16)
            frame_int16[noise_mask] += noise[noise_mask]
            
            # Clip and convert back
            processed_frame = np.clip(frame_int16, 0, 255).astype(np.uint8)
            processed_frames.append(processed_frame)
        
        return processed_frames
    
    def re_encode_video(self, input_path: str, output_path: str, crf: int = 27) -> bool:
        """Re-encode video with hardware acceleration"""
        try:
            if self.hardware_encoder == 'h264_videotoolbox':
                cmd = [
                    'ffmpeg', '-i', input_path,
                    '-c:v', 'h264_videotoolbox',
                    '-b:v', f'{self._crf_to_bitrate(crf)}k',
                    '-profile:v', 'main',
                    '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '128k',
                    '-movflags', '+faststart',
                    '-threads', str(self.max_threads),
                    '-y', output_path
                ]
            else:
                cmd = [
                    'ffmpeg', '-i', input_path,
                    '-c:v', 'libx264', '-crf', str(crf),
                    '-preset', 'medium',
                    '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '128k',
                    '-movflags', '+faststart',
                    '-threads', str(self.max_threads),
                    '-y', output_path
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _crf_to_bitrate(self, crf: int) -> int:
        """Convert CRF to bitrate"""
        crf_bitrate_map = {
            18: 8000, 20: 6000, 23: 4000, 27: 2500, 30: 1500, 32: 1000, 35: 800
        }
        return crf_bitrate_map.get(crf, 2500)
    
    def process_video(self, input_file_path: str, options: dict) -> Tuple[bool, str, str]:
        """Main processing pipeline - returns (success, message, output_filename)"""
        try:
            output_filename = self.generate_random_filename()
            final_output = self.output_dir / output_filename
            
            current_file = input_file_path
            temp_files = []
            
            # Processing pipeline
            if options.get('strip_metadata', False):
                temp_file = self.temp_dir / f"step1_{output_filename}"
                temp_files.append(temp_file)
                
                if not self.strip_metadata(current_file, str(temp_file)):
                    return False, "Failed to strip metadata", ""
                current_file = str(temp_file)
            
            if options.get('add_noise', False):
                temp_file = self.temp_dir / f"step2_{output_filename}"
                temp_files.append(temp_file)
                
                if not self.add_pixel_noise(current_file, str(temp_file), options.get('noise_intensity', 2)):
                    return False, "Failed to add pixel noise", ""
                current_file = str(temp_file)
            
            if options.get('re_encode', False):
                temp_file = self.temp_dir / f"step3_{output_filename}"
                temp_files.append(temp_file)
                
                if not self.re_encode_video(current_file, str(temp_file), options.get('crf_value', 27)):
                    return False, "Failed to re-encode video", ""
                current_file = str(temp_file)
            
            # Copy to final output
            shutil.copy2(current_file, str(final_output))
            
            # Cleanup temp files
            for temp_file in temp_files:
                if temp_file.exists():
                    temp_file.unlink()
            
            return True, f"Video processed successfully", output_filename
            
        except Exception as e:
            return False, f"Processing error: {str(e)}", ""


# Initialize FastAPI app
app = FastAPI(title="Aura Farming Video Processor API", version="1.0.0")

# Add CORS middleware for Railway frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your Railway domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processor
processor = VideoProcessor()

# Store processing status
processing_status = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Aura Farming Video Processor API",
        "platform": "DigitalOcean",
        "version": "1.0.0"
    }

@app.get("/status")
async def status():
    """System status endpoint"""
    return {
        "hardware_encoder": processor.hardware_encoder,
        "max_threads": processor.max_threads,
        "platform": "digitalocean",
        "memory_optimized": True
    }

@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """Upload video for processing"""
    
    # Validate file
    if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Check file size (200MB limit)
    if file.size > 200 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 200MB)")
    
    # Generate unique job ID
    job_id = f"job_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Save uploaded file
    input_filename = f"{job_id}_{file.filename}"
    input_path = processor.input_dir / input_filename
    
    try:
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Initialize job status
        processing_status[job_id] = {
            "status": "uploaded",
            "filename": file.filename,
            "input_path": str(input_path),
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "job_id": job_id,
            "status": "uploaded",
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/process/{job_id}")
async def process_video(
    job_id: str,
    options: dict = None
):
    """Process uploaded video"""
    
    if job_id not in processing_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = processing_status[job_id]
    
    if job["status"] != "uploaded":
        raise HTTPException(status_code=400, detail="Job already processed or in progress")
    
    # Default options
    if options is None:
        options = {
            "strip_metadata": True,
            "add_noise": True,
            "re_encode": True,
            "noise_intensity": 2,
            "crf_value": 27
        }
    
    try:
        # Update status
        processing_status[job_id]["status"] = "processing"
        processing_status[job_id]["started_at"] = datetime.now().isoformat()
        
        # Process video
        success, message, output_filename = processor.process_video(
            job["input_path"], 
            options
        )
        
        if success:
            processing_status[job_id].update({
                "status": "completed",
                "output_filename": output_filename,
                "completed_at": datetime.now().isoformat(),
                "message": message
            })
            
            return {
                "job_id": job_id,
                "status": "completed",
                "output_filename": output_filename,
                "download_url": f"/download/{output_filename}"
            }
        else:
            processing_status[job_id].update({
                "status": "failed",
                "error": message,
                "failed_at": datetime.now().isoformat()
            })
            
            raise HTTPException(status_code=500, detail=message)
            
    except Exception as e:
        processing_status[job_id].update({
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        })
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Get job status"""
    if job_id not in processing_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return processing_status[job_id]

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download processed video"""
    file_path = processor.output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='video/mp4'
    )

@app.delete("/cleanup/{job_id}")
async def cleanup_job(job_id: str):
    """Clean up job files"""
    if job_id not in processing_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = processing_status[job_id]
    
    # Clean up input file
    input_path = Path(job.get("input_path", ""))
    if input_path.exists():
        input_path.unlink()
    
    # Clean up output file
    output_filename = job.get("output_filename")
    if output_filename:
        output_path = processor.output_dir / output_filename
        if output_path.exists():
            output_path.unlink()
    
    # Remove from status
    del processing_status[job_id]
    
    return {"message": "Job cleaned up successfully"}

if __name__ == "__main__":
    # DigitalOcean port
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)