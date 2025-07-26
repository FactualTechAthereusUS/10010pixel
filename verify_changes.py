#!/usr/bin/env python3
"""
Video Change Verification Script
Compares original vs processed videos to verify changes are being made
"""

import hashlib
import cv2
import numpy as np
import subprocess
import json
from pathlib import Path
import argparse

def get_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """Calculate file hash"""
    hash_func = getattr(hashlib, algorithm)()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

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
    cap.set(cv2.CAP_PROP_POS_FRAMES, stats['frame_count'] - 1)
    ret, frame = cap.read()
    if ret:
        stats['last_frame_hash'] = hashlib.md5(frame.tobytes()).hexdigest()
    
    cap.release()
    return stats

def compare_videos(original_path: str, processed_path: str) -> dict:
    """Compare original and processed videos"""
    print(f"\n🔍 Comparing Videos:")
    print(f"  Original: {Path(original_path).name}")
    print(f"  Processed: {Path(processed_path).name}")
    
    # File hashes
    original_hash = get_file_hash(original_path)
    processed_hash = get_file_hash(processed_path)
    
    # Video stats
    original_stats = get_video_stats(original_path)
    processed_stats = get_video_stats(processed_path)
    
    # Metadata
    original_metadata = get_video_metadata(original_path)
    processed_metadata = get_video_metadata(processed_path)
    
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
        'processed_stats': processed_stats
    }
    
    return comparison

def print_comparison_results(comparison: dict):
    """Print detailed comparison results"""
    print("\n📊 VERIFICATION RESULTS:")
    print("=" * 50)
    
    changes = [
        ("File Hash Changed", comparison['file_hash_changed']),
        ("First Frame Changed", comparison['first_frame_changed']),
        ("Last Frame Changed", comparison['last_frame_changed']),
        ("Metadata Changed", comparison['metadata_changed']),
        ("Duration Changed", comparison['duration_changed']),
        ("Resolution Changed", comparison['resolution_changed'])
    ]
    
    any_changes = any(change[1] for change in changes)
    
    for name, changed in changes:
        status = "✅ YES" if changed else "❌ NO"
        print(f"  {name:<20}: {status}")
    
    print("\n" + "=" * 50)
    if any_changes:
        print("🎉 VIDEO SUCCESSFULLY MODIFIED!")
        print("   The processed video has a different digital fingerprint.")
    else:
        print("⚠️  NO CHANGES DETECTED!")
        print("   The videos appear identical. Check processing settings.")
    
    print(f"\n📋 TECHNICAL DETAILS:")
    print(f"  Original Hash: {comparison['original_hash'][:16]}...")
    print(f"  Processed Hash: {comparison['processed_hash'][:16]}...")
    
    orig_stats = comparison['original_stats']
    proc_stats = comparison['processed_stats']
    
    print(f"  Resolution: {orig_stats['width']}x{orig_stats['height']} → {proc_stats['width']}x{proc_stats['height']}")
    print(f"  Duration: {orig_stats['duration']:.2f}s → {proc_stats['duration']:.2f}s")
    print(f"  Frame Count: {orig_stats['frame_count']} → {proc_stats['frame_count']}")

def auto_verify_output_folder():
    """Automatically verify all videos in output folder"""
    input_dir = Path("input")
    output_dir = Path("output")
    
    if not input_dir.exists() or not output_dir.exists():
        print("❌ Input or output directories not found!")
        return
    
    input_videos = list(input_dir.glob("*.*"))
    output_videos = list(output_dir.glob("*.*"))
    
    if not input_videos:
        print("❌ No videos found in input/ folder!")
        print("   Add some videos to input/ and process them first.")
        return
    
    if not output_videos:
        print("❌ No processed videos found in output/ folder!")
        print("   Process some videos first using the main app.")
        return
    
    print(f"📁 Found {len(input_videos)} input videos and {len(output_videos)} output videos")
    
    if len(input_videos) == 1 and len(output_videos) >= 1:
        # Compare single input with latest output
        original = input_videos[0]
        processed = max(output_videos, key=lambda x: x.stat().st_mtime)
        
        comparison = compare_videos(str(original), str(processed))
        print_comparison_results(comparison)
    else:
        print("\n💡 Manual verification recommended:")
        print("   Use: python verify_changes.py original_video.mp4 processed_video.mp4")

def main():
    parser = argparse.ArgumentParser(description='Verify video processing changes')
    parser.add_argument('original', nargs='?', help='Original video file')
    parser.add_argument('processed', nargs='?', help='Processed video file')
    parser.add_argument('--auto', action='store_true', help='Auto-verify output folder')
    
    args = parser.parse_args()
    
    if args.auto or (not args.original and not args.processed):
        auto_verify_output_folder()
    elif args.original and args.processed:
        if not Path(args.original).exists():
            print(f"❌ Original file not found: {args.original}")
            return
        if not Path(args.processed).exists():
            print(f"❌ Processed file not found: {args.processed}")
            return
        
        comparison = compare_videos(args.original, args.processed)
        print_comparison_results(comparison)
    else:
        print("Usage:")
        print("  python verify_changes.py original.mp4 processed.mp4")
        print("  python verify_changes.py --auto")

if __name__ == "__main__":
    main() 