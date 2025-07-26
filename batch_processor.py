#!/usr/bin/env python3
"""
Command-line batch processor for TikTok Video Processor
Usage: python batch_processor.py [input_directory] [options]
"""

import argparse
import os
import sys
from pathlib import Path
import logging
from typing import List

# Import the VideoProcessor from main app
from app import VideoProcessor

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

def find_video_files(directory: Path) -> List[Path]:
    """Find all video files in directory"""
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v', '.flv'}
    video_files = []
    
    for file_path in directory.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in video_extensions:
            video_files.append(file_path)
    
    return sorted(video_files)

def main():
    parser = argparse.ArgumentParser(
        description='Batch process videos to create unique digital fingerprints',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_processor.py input/                    # Process all videos in input/ folder
  python batch_processor.py input/ --no-noise        # Skip pixel noise addition
  python batch_processor.py input/ --crf 23          # Use CRF 23 for re-encoding
  python batch_processor.py input/ --silence         # Add silence padding
        """
    )
    
    parser.add_argument('input_dir', 
                       help='Directory containing video files to process')
    
    # Processing options
    parser.add_argument('--no-metadata', action='store_true',
                       help='Skip metadata stripping (default: enabled)')
    parser.add_argument('--no-noise', action='store_true',
                       help='Skip pixel noise addition (default: enabled)')
    parser.add_argument('--no-reencode', action='store_true',
                       help='Skip video re-encoding (default: enabled)')
    parser.add_argument('--silence', action='store_true',
                       help='Add silence padding (default: disabled)')
    parser.add_argument('--overlay', action='store_true',
                       help='Add transparent overlay (default: disabled)')
    
    # Settings
    parser.add_argument('--noise-intensity', type=int, default=2, choices=range(1, 6),
                       help='Pixel noise intensity (1-5, default: 2)')
    parser.add_argument('--crf', type=int, default=27, choices=range(18, 36),
                       help='CRF value for re-encoding (18-35, default: 27)')
    parser.add_argument('--silence-duration', type=float, default=0.2,
                       help='Silence duration in seconds (default: 0.2)')
    
    # Output options
    parser.add_argument('--output-dir', default='output',
                       help='Output directory (default: output)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be processed without actually processing')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Validate input directory
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        sys.exit(1)
    
    if not input_dir.is_dir():
        logger.error(f"Input path is not a directory: {input_dir}")
        sys.exit(1)
    
    # Find video files
    video_files = find_video_files(input_dir)
    if not video_files:
        logger.warning(f"No video files found in {input_dir}")
        sys.exit(0)
    
    logger.info(f"Found {len(video_files)} video files")
    
    if args.dry_run:
        logger.info("DRY RUN - Files that would be processed:")
        for video_file in video_files:
            logger.info(f"  {video_file}")
        sys.exit(0)
    
    # Setup processor
    processor = VideoProcessor()
    
    # Override output directory if specified
    if args.output_dir != 'output':
        processor.output_dir = Path(args.output_dir)
        processor.output_dir.mkdir(exist_ok=True)
    
    # Build options dict
    options = {
        'strip_metadata': not args.no_metadata,
        'add_noise': not args.no_noise,
        're_encode': not args.no_reencode,
        'add_silence': args.silence,
        'add_overlay': args.overlay,
        'noise_intensity': args.noise_intensity,
        'crf_value': args.crf,
        'silence_duration': args.silence_duration,
    }
    
    # Log processing options
    logger.info("Processing options:")
    for key, value in options.items():
        logger.info(f"  {key}: {value}")
    
    # Process videos
    success_count = 0
    error_count = 0
    
    for i, video_file in enumerate(video_files, 1):
        logger.info(f"Processing [{i}/{len(video_files)}]: {video_file.name}")
        
        try:
            success, message = processor.process_video(str(video_file), options)
            
            if success:
                success_count += 1
                logger.info(message)
            else:
                error_count += 1
                logger.error(message)
                
        except KeyboardInterrupt:
            logger.warning("Processing interrupted by user")
            break
        except Exception as e:
            error_count += 1
            logger.error(f"Unexpected error processing {video_file.name}: {e}")
    
    # Summary
    logger.info(f"\nProcessing complete:")
    logger.info(f"  ✅ Success: {success_count}")
    logger.info(f"  ❌ Errors: {error_count}")
    logger.info(f"  📁 Output directory: {processor.output_dir.absolute()}")

if __name__ == "__main__":
    main() 