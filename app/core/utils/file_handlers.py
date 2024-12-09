import os
import shutil
from pathlib import Path

class FileManager:
    """Utility class for file operations."""
    
    @staticmethod
    def ensure_directory_exists(directory):
        """Create directory if it doesn't exist."""
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def safe_filename(filename):
        """
        Create a safe filename, removing potentially dangerous characters.
        Args:
            filename: Original filename
        Returns:
            str: Sanitized filename
        """
        # Remove potentially dangerous characters
        safe_chars = [c for c in filename if c.isalnum() or c in '._- ']
        return ''.join(safe_chars).strip()
    
    @staticmethod
    def get_available_filename(directory, filename):
        """
        Get an available filename by appending numbers if necessary.
        Args:
            directory: Target directory
            filename: Desired filename
        Returns:
            str: Available filename
        """
        base, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename
        
        while os.path.exists(os.path.join(directory, new_filename)):
            new_filename = f"{base}_{counter}{ext}"
            counter += 1
            
        return new_filename

# utils/video_helpers.py
import subprocess
from typing import Dict, Any

class VideoInfo:
    """Utility class for getting video information."""
    
    @staticmethod
    def get_video_metadata(file_path: str) -> Dict[str, Any]:
        """
        Get video metadata using ffprobe.
        Args:
            file_path: Path to video file
        Returns:
            dict: Video metadata including duration, resolution, codec, etc.
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                metadata = json.loads(result.stdout)
                
                # Extract relevant information
                video_stream = next(
                    (s for s in metadata['streams'] if s['codec_type'] == 'video'),
                    None
                )
                
                if video_stream:
                    return {
                        'duration': float(metadata['format'].get('duration', 0)),
                        'size': int(metadata['format'].get('size', 0)),
                        'bitrate': int(metadata['format'].get('bit_rate', 0)),
                        'width': int(video_stream.get('width', 0)),
                        'height': int(video_stream.get('height', 0)),
                        'codec': video_stream.get('codec_name', 'unknown'),
                        'fps': eval(video_stream.get('r_frame_rate', '0/1'))
                    }
                    
            return {}
            
        except Exception as e:
            print(f"Error getting video metadata: {str(e)}")
            return {}
