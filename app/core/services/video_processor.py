import os
import json
import logging
import subprocess
from datetime import datetime
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

from django.core.exceptions import ValidationError

from ..utils.validators import VideoValidator
from ..utils.exceptions import VideoProcessingError, StorageError, DuplicateTitleError, InvalidVideoError
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
        """Convert video to DASH format."""
        output_path = os.path.join(self.storage.mpd_root, f"{title}.mpd")
        
        command = [
            'ffmpeg', '-i', file_path,
            '-map', '0',
            '-s:v', '1920x1080',
            '-c:v', 'libx264',
            '-b:v', '2400k',
            '-an',
            '-f', 'dash',
            '-seg_duration', '4',
            '-adaptation_sets', 'id=0,streams=v',
            '-use_template', '1',
            '-use_timeline', '1',
            output_path
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Add BaseURL to the MPD file
            self._add_base_url_to_mpd(output_path, title)
            
        return result

    def _add_base_url_to_mpd(self, mpd_path, title):
        """Add BaseURL element to MPD file."""
        try:
            # Parse the MPD file
            tree = ET.parse(mpd_path)
            root = tree.getroot()
            
            # Create BaseURL element
            # This URL should match your segment endpoint pattern
            base_url = f"/api/videos/{title}/segments/"
            
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

