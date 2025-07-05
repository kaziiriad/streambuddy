import os
import json
import logging
import subprocess
import math
from datetime import datetime
import time
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from django.conf import settings

from django.core.exceptions import ValidationError
from streambuddy_common.utils.progress_tracker import FFmpegProgress
from streambuddy_common.utils.validators import VideoValidator
from streambuddy_common.exceptions import VideoProcessingError, StorageError, DuplicateTitleError, InvalidVideoError
from .storage import StorageService

class VideoProcessor:
    def __init__(self):
        self.storage = StorageService()

    def process_upload(self, file, title):
        """Handle the complete upload and processing flow."""
        temp_path = None
        try:
            logging.info(f"Starting video upload process for {title}")
            
            # Validate video file
            try:
                VideoValidator.validate_video_file(file)
                logging.info("Video validation passed")
            except ValidationError as e:
                logging.error(f"Video validation failed: {str(e)}")
                raise InvalidVideoError(str(e))

            # Check for existing video
            existing_metadata = self.storage.get_metadata(title)
            if existing_metadata:
                logging.warning(f"Duplicate title found: {title}")
                raise DuplicateTitleError()

            # Create initial metadata
            metadata = {
                'title': title,
                'original_filename': file.name,
                'uploaded_at': str(datetime.now()),
                'processed': False,
                'status': 'uploading'
            }

            # Save initial metadata
            logging.info("Saving initial metadata")
            self.storage.save_metadata(title, metadata)

            # Save uploaded file
            logging.info("Saving temporary file")
            temp_path = self.storage.save_temp_upload(file, title)

            # Process video
            logging.info("Starting video processing")
            result = self.process_to_dash(temp_path, title)
            
            if result.returncode != 0:
                error_msg = f"FFMPEG error: {result.stderr}"
                logging.error(error_msg)
                raise VideoProcessingError(error_msg)

            # Update metadata after successful processing
            logging.info("Updating metadata after successful processing")
            metadata.update({
                'processed': True,
                'status': 'completed',
                'mpd_file': self.storage.get_mpd_path(title)
            })
            self.storage.save_metadata(title, metadata)

            logging.info(f"Video processing completed successfully for {title}")
            return metadata

        except Exception as e:
            logging.error(f"Error in process_upload: {str(e)}")
            
            # Cleanup temporary file if it exists
            if temp_path and os.path.exists(temp_path):
                try:
                    self.storage.cleanup_temp_file(temp_path)
                except Exception as cleanup_error:
                    logging.error(f"Error during cleanup: {str(cleanup_error)}")
            
            # Update metadata to reflect failure
            try:
                metadata = {
                    'title': title,
                    'original_filename': file.name,
                    'uploaded_at': str(datetime.now()),
                    'processed': False,
                    'status': 'failed',
                    'error': str(e)
                }
                self.storage.save_metadata(title, metadata)
            except Exception as metadata_error:
                logging.error(f"Error updating failure metadata: {str(metadata_error)}")

            # Re-raise appropriate exception
            if isinstance(e, (VideoProcessingError, StorageError, InvalidVideoError, DuplicateTitleError)):
                raise
            raise VideoProcessingError(str(e))
        
        finally:
            # Always cleanup temporary file
            if temp_path:
                try:
                    logging.info(f"Cleaning up temporary file: {temp_path}")
                    self.storage.cleanup_temp_file(temp_path)
                except Exception as e:
                    logging.error(f"Failed to cleanup temporary file: {str(e)}")


    def process_to_dash(self, file_path, title):
        """Convert video to DASH format with single 1080p quality."""
        try:
            output_dir = os.path.join(self.storage.mpd_root, title)  # Create subfolder for each video
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{title}.mpd")
            
            command = [
            'ffmpeg', '-i', file_path,
            # 1080p
            '-map', '0:v', '-s:v:0', '1920x1080',
            '-c:v:0', 'libx264', '-b:v:0', '5000k',
            '-maxrate:v:0', '5500k', '-bufsize:v:0', '10000k',
            
            # 720p
            '-map', '0:v', '-s:v:1', '1280x720',
            '-c:v:1', 'libx264', '-b:v:1', '2800k',
            '-maxrate:v:1', '3300k', '-bufsize:v:1', '6000k',
            
            # 480p
            '-map', '0:v', '-s:v:2', '854x480',
            '-c:v:2', 'libx264', '-b:v:2', '1400k',
            '-maxrate:v:2', '1750k', '-bufsize:v:2', '2800k',
            
            # Common settings
            '-preset', 'veryfast',  # Fast encoding
            '-profile:v', 'main',
            '-keyint_min', '48',
            '-g', '48',  # Keyframe interval
            '-sc_threshold', '0',  # Disable scene cut detection
            '-b_strategy', '0',
            
            # DASH settings
            '-f', 'dash',
            '-init_seg_name', f'init-$RepresentationID$.m4s',
            '-media_seg_name', f'chunk-$RepresentationID$-$Number%05d$.m4s',
            '-adaptation_sets', 'id=0,streams=v',
            '-use_template', '1',
            '-use_timeline', '1',
            '-seg_duration', '4',
            output_path
        ]


            result = subprocess.run(command, capture_output=True, text=True)
                
            if result.returncode == 0:
                self._add_base_url_to_mpd(output_path, title)
                metadata = self.storage.get_metadata(title) or {}
                metadata.update({
                    'status': 'completed',
                    'processing_progress': 100,
                    'completed_at': str(datetime.now()),
                    'mpd_file': f"{title}.mpd",
                    'title': title,
                    'resolutions': ['1080p', '720p', '480p']  # Add available resolutions
                })
                self.storage.save_metadata(title, metadata)
                return result
            else:
                raise Exception(f"DASH creation failed: {result.stderr}")
            
        except Exception as e:
            logging.error(f"Error in process_to_dash: {str(e)}")
            raise

    def _add_base_url_to_mpd(self, mpd_path, title):
        """Add BaseURL element to MPD file."""
        try:
            # Parse the MPD file
            tree = ET.parse(mpd_path)
            root = tree.getroot()
            
            # Create BaseURL element
            # This URL should match your segment endpoint pattern
            base_url = f"/api/videos/{title}/segments"
            
            # Check if BaseURL already exists
            existing_base_url = root.find('{*}BaseURL')
            if existing_base_url is not None:
                existing_base_url.text = base_url
            else:
                # Add BaseURL after Period element
                base_url_elem = ET.Element('BaseURL')
                base_url_elem.text = base_url
                root.insert(0, base_url_elem)
            
            # Write the modified XML back to the file
            tree.write(mpd_path, encoding='utf-8', xml_declaration=True)
            
        except Exception as e:
            logging.error(f"Error adding BaseURL to MPD: {str(e)}")
            raise

    def get_video_info(self, title):
        """Get video metadata."""
        return self.storage.get_metadata(title)

