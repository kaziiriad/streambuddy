import logging
import re
import time
from datetime import datetime
import json
import os

class FFmpegProgress:
    def __init__(self, total_duration, storage_service, title):
        self.total_duration = total_duration
        self.storage_service = storage_service
        self.title = title
        self.start_time = time.time()

    def update_progress(self, progress_text):
        """Update progress based on FFmpeg output."""
        try:
            # Parse FFmpeg progress output
            time_match = re.search(r"time=(\d+:\d+:\d+.\d+)", progress_text)
            if time_match:
                current_time = time_match.group(1)
                # Convert HH:MM:SS.MS to seconds
                h, m, s = current_time.split(':')
                s = float(s)
                current_seconds = float(h) * 3600 + float(m) * 60 + s
                
                # Calculate progress percentage
                progress = min(100, (current_seconds / self.total_duration) * 100)
                
                # Calculate estimated time remaining
                elapsed_time = time.time() - self.start_time
                if progress > 0:
                    total_estimated_time = elapsed_time * (100 / progress)
                    remaining_time = total_estimated_time - elapsed_time
                else:
                    remaining_time = 0

                # Update metadata with progress
                self._update_metadata(progress, remaining_time)
                
                return progress
        except Exception as e:
            print(f"Error updating progress: {str(e)}")
        return 0

    def _update_metadata(self, progress, remaining_time):
        """Update video metadata with progress information."""
        try:
            metadata = self.storage_service.get_metadata(self.title)
            if metadata:
                # Keep all existing metadata and update progress information
                metadata.update({
                    'processing_progress': round(progress, 2),
                    'estimated_time_remaining': round(remaining_time),
                    'last_updated': str(datetime.now()),
                    # Preserve essential fields
                    'title': metadata.get('title', self.title),
                    'display_title': metadata.get('display_title', self.title),
                    'original_filename': metadata.get('original_filename'),
                    'uploaded_at': metadata.get('uploaded_at'),
                    'status': metadata.get('status', 'processing'),
                    'processed': metadata.get('processed', False)
                })
                self.storage_service.save_metadata(self.title, metadata)
        except Exception as e:
            logging.error(f"Error updating metadata: {str(e)}")