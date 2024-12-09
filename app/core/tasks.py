from streambuddy.celery import app
from celery import shared_task
# ... rest of your tasks code remains the same ...from .services.video_processor import VideoProcessor
from .services.storage import StorageService
from .services.video_processor import VideoProcessor
from datetime import datetime
import logging


@shared_task(bind=True)
def process_video_task(self, file_path, title):
    """
    Celery task for processing video files.
    """
    processor = VideoProcessor()
    storage = StorageService()
    
    try:
        # Update metadata to show processing has started
        metadata = storage.get_metadata(title)
        metadata.update({
            'status': 'processing',
            'task_id': self.request.id,
            'processing_started': str(datetime.now())
        })
        storage.save_metadata(title, metadata)
        
        # Process the video
        result = processor.process_to_dash(file_path, title)
        
        if result.returncode != 0:
            raise Exception(f"FFMPEG error: {result.stderr}")

        # Update metadata after successful processing
        metadata.update({
            'processed': True,
            'status': 'completed',
            'mpd_file': storage.get_mpd_path(title),
            'processing_completed': str(datetime.now())
        })
        storage.save_metadata(title, metadata)
        
        # Cleanup temporary file
        storage.cleanup_temp_file(file_path)
        
        return {
            'status': 'success',
            'title': title,
            'message': 'Video processing completed successfully'
        }
        
    except Exception as e:
        logging.error(f"Error processing video {title}: {str(e)}")
        
        # Update metadata to reflect failure
        try:
            metadata.update({
                'status': 'failed',
                'error': str(e),
                'processing_completed': str(datetime.now())
            })
            storage.save_metadata(title, metadata)
        except Exception as metadata_error:
            logging.error(f"Error updating metadata: {str(metadata_error)}")
            
        # Ensure temp file is cleaned up even on failure
        try:
            storage.cleanup_temp_file(file_path)
        except Exception as cleanup_error:
            logging.error(f"Error cleaning up temp file: {str(cleanup_error)}")
            
        raise