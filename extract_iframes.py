import os
import subprocess
import re
import argparse
from pathlib import Path

def is_valid_filename_pattern(filename):
    """
    Check if filename matches the pattern {nr}_{name}.ext
    Returns a match object if valid, None otherwise
    """
    pattern = r'^(\d+)_([^.]+)\.(.+)$'
    return re.match(pattern, filename)

def extract_iframes(input_file, frames_dir, output_pattern):
    """
    Extract I-frames from video file using ffmpeg
    
    Args:
        input_file (str): Path to input video file
        frames_dir (Path): Directory to store extracted frames
        output_pattern (str): Pattern for output jpg files
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create frames directory if it doesn't exist
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        # Full path for output pattern
        output_path = str(frames_dir / output_pattern)
        
        cmd = [
            'ffmpeg',
            '-i', str(input_file),
            '-vf', "select='eq(pict_type,I)'",
            '-fps_mode', 'vfr',
            output_path
        ]
        
        # Run ffmpeg command and capture output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error processing {input_file}:")
            print(result.stderr)
            return False
            
        return True
        
    except subprocess.SubprocessError as e:
        print(f"Failed to process {input_file}: {str(e)}")
        return False
    except OSError as e:
        print(f"Failed to create frames directory: {str(e)}")
        return False

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Extract I-frames from videos matching pattern {nr}_{name}.ext'
    )
    parser.add_argument(
        '--directory',
        '-d',
        default='.',
        help='Directory to process (default: current directory)'
    )
    args = parser.parse_args()
    
    # Ensure directory exists
    work_dir = Path(args.directory)
    if not work_dir.is_dir():
        print(f"Error: Directory '{args.directory}' does not exist")
        return 1
    
    # Create frames directory
    frames_dir = work_dir / 'frames'
    
    # Process all files in directory
    processed_count = 0
    error_count = 0
    
    for file_path in work_dir.iterdir():
        if not file_path.is_file():
            continue
            
        match = is_valid_filename_pattern(file_path.name)
        if not match:
            continue
            
        # Extract components from filename
        nr, name, ext = match.groups()
        
        print(f"Processing {file_path.name}...")
        
        # Create output pattern for this file
        output_pattern = f"{nr}_{name}-%d.jpg"
        
        # Process the file
        if extract_iframes(file_path, frames_dir, output_pattern):
            processed_count += 1
            print(f"Saved frames to {frames_dir / nr}_{name}-*.jpg")
        else:
            error_count += 1
    
    # Print summary
    print("\nProcessing complete!")
    print(f"Successfully processed: {processed_count} files")
    print(f"Frames saved in: {frames_dir}")
    if error_count > 0:
        print(f"Errors encountered: {error_count} files")
    
    return 0 if error_count == 0 else 1

if __name__ == "__main__":
    exit(main())
