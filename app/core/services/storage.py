import os
import json
import boto3
from datetime import datetime
from django.conf import settings
from ..utils.exceptions import StorageError, VideoNotFoundError
import logging

class StorageService:
    """Service class for handling both local and S3 storage operations."""
    
    def __init__(self):
        # Initialize local storage paths
        self.metadata_root = os.path.join(settings.MEDIA_ROOT, 'metadata')
        self.mpd_root = os.path.join(settings.MEDIA_ROOT, 'dash_output')
        self.temp_upload_root = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
        
        # Create necessary directories
        for directory in [self.metadata_root, self.mpd_root, self.temp_upload_root]:
            os.makedirs(directory, exist_ok=True)
        
        # Initialize S3 client if configured
        self.use_s3 = getattr(settings, 'USE_S3', False)
        if self.use_s3:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def upload_video(self, file_obj, key):
        """Upload video file to storage."""
        try:
            if self.use_s3:
                self.s3_client.upload_fileobj(
                    file_obj,
                    self.bucket_name,
                    f"videos/{key}"
                )
                return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/videos/{key}"
            else:
                return self.save_temp_upload(file_obj, key)
        except Exception as e:
            raise StorageError(f"Failed to upload video: {str(e)}")


    def get_metadata(self, title):
        """Retrieve video metadata from local storage."""
        metadata_path = os.path.join(self.metadata_root, f"{title}.json")
        
        if not os.path.exists(metadata_path):
            logging.info(f"No metadata file found at {metadata_path}")
            return None
            
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Corrupted metadata file for {title}: {str(e)}")
            raise StorageError(f"Corrupted metadata file: {str(e)}")
        except Exception as e:
            logging.error(f"Error reading metadata for {title}: {str(e)}")
            raise StorageError(f"Error reading metadata: {str(e)}")


    def save_metadata(self, title, metadata):
        """Save video metadata to local storage."""
        try:
            metadata_path = os.path.join(self.metadata_root, f"{title}.json")
            logging.info(f"Saving metadata to {metadata_path}")
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
            
            logging.info(f"Successfully saved metadata for {title}")
        except Exception as e:
            logging.error(f"Failed to save metadata for {title}: {str(e)}")
            raise StorageError(f"Failed to save metadata: {str(e)}")

    def save_mpd(self, title, mpd_file):
        """Save MPD file to local storage."""
        try:
            dest_path = os.path.join(self.mpd_root, f"{title}.mpd")
            os.rename(mpd_file, dest_path)
            return dest_path
        except Exception as e:
            raise StorageError(f"Failed to save MPD file: {str(e)}")

    def get_mpd_path(self, title):
        """Get MPD file path."""
        mpd_path = os.path.join(self.mpd_root, f"{title}.mpd")
        if not os.path.exists(mpd_path):
            raise VideoNotFoundError(f"MPD file not found for video: {title}")
        return mpd_path

    def get_segment_path(self, segment_name):
        """Get segment file path."""
        segment_path = os.path.join(self.mpd_root, segment_name)
        if not os.path.exists(segment_path):
            raise VideoNotFoundError(f"Segment not found: {segment_name}")
        return segment_path

    def save_temp_upload(self, file, title):
        """Save uploaded file to temporary location."""
        try:
            file_path = os.path.join(self.temp_upload_root, f"{title}_{file.name}")
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            return file_path
        except Exception as e:
            raise StorageError(f"Failed to save temporary file: {str(e)}")

    def cleanup_temp_file(self, file_path):
        """Remove temporary upload file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            raise StorageError(f"Failed to cleanup temporary file: {str(e)}")

    def list_videos(self):
        """List all available videos."""
        try:
            videos = []
            for filename in os.listdir(self.metadata_root):
                if filename.endswith('.json'):
                    with open(os.path.join(self.metadata_root, filename)) as f:
                        videos.append(json.load(f))
            return videos
        except Exception as e:
            raise StorageError(f"Failed to list videos: {str(e)}")

    def delete_video(self, title):
        """Delete video and all associated files."""
        try:
            # Delete metadata
            metadata_path = os.path.join(self.metadata_root, f"{title}.json")
            if os.path.exists(metadata_path):
                os.remove(metadata_path)

            # Delete MPD and segments
            mpd_path = os.path.join(self.mpd_root, f"{title}.mpd")
            if os.path.exists(mpd_path):
                os.remove(mpd_path)
                
            # Delete segments (they typically follow a pattern)
            segment_pattern = f"{title}_*.m4s"
            for segment in os.listdir(self.mpd_root):
                if segment.startswith(title):
                    os.remove(os.path.join(self.mpd_root, segment))

            # Delete from S3 if using it
            if self.use_s3:
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=f"videos/{title}"
                )
                
        except Exception as e:
            raise StorageError(f"Failed to delete video: {str(e)}")

    def save_metadata(self, title, metadata):
        """Save video metadata to local storage."""
        try:
            # Ensure metadata directory exists
            os.makedirs(self.metadata_root, exist_ok=True)
            
            metadata_path = os.path.join(self.metadata_root, f"{title}.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
        except Exception as e:
            raise StorageError(f"Failed to save metadata: {str(e)}")

    def check_title_exists(self, title):
        """Check if a video with this title already exists."""
        metadata_path = os.path.join(self.metadata_root, f"{title}.json")
        return os.path.exists(metadata_path)
