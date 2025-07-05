from streambuddy.celery import app
from celery import shared_task
# ... rest of your tasks code remains the same ...from .services.video_processor import VideoProcessor
from .services.storage import StorageService
from streambuddy_common.utils.progress_tracker import FFmpegProgress
from datetime import datetime
import logging
from celery import Task
import os


class VideoProcessingTask(Task):
    name = 'process_video'
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        title = args[1] if len(args) > 1 else None
        if title:
            storage = StorageService()
            try:
                # Get existing metadata and update it
                metadata = storage.get_metadata(title) or {'title': title}
                metadata.update({
                    'status': 'failed',
                    'error': str(exc),
                    'completed_at': str(datetime.now())
                })
                storage.save_metadata(title, metadata)
            except Exception as e:
                logging.error(f"Failed to update metadata on failure: {str(e)}")

@shared_task(base=VideoProcessingTask, bind=True)
def process_video_task(self, file_path, title):
    """Celery task for processing video files with progress tracking."""
    processor = VideoProcessor()
    storage = StorageService()
    
    try:
        # Set lower nice value for FFmpeg process
        os.nice(10)
        
        # Get and update metadata while preserving fields
        metadata = storage.get_metadata(title)
        if not metadata:
            metadata = {
                'title': title,
                'uploaded_at': str(datetime.now()),
                'original_filename': os.path.basename(file_path)
            }
        
        metadata.update({
            'status': 'processing',
            'task_id': self.request.id,
            'processing_started': str(datetime.now()),
            'progress': 0
        })
        storage.save_metadata(title, metadata)
        
        # Get video duration and set up progress tracking
        # Process video with progress tracking
        result = processor.process_to_dash(file_path, title)

        

        # if result.returncode != 0:
        #     raise Exception(f"FFMPEG error: {result.stderr}")

        # # Update completion metadata
        # metadata = storage.get_metadata(title)
        # metadata.update({
        #     'processed': True,
        #     'status': 'completed',
        #     'processing_completed': str(datetime.now()),
        #     'mpd_file': f"{title}.mpd"  # Add MPD file reference
        # })
        # storage.save_metadata(title, metadata)
        
        # Cleanup
        storage.cleanup_temp_file(file_path)
        
        return {
            'processed': True,
            'status': 'success',
            'title': title,
            'processing_completed': str(datetime.now()),
            'message': 'Video processing completed successfully',
            'mpd_url': f"/api/videos/{title}/mpd/"
        }
        
    except Exception as e:
        logging.error(f"Video processing failed for {title}: {str(e)}")
        # Let the on_failure handler deal with metadata update
        raise

@shared_task
def monitor_worker_health():
    inspector = app.control.inspect()
    active = inspector.active()
    
    if not active:
        logging.error("Celery workers are down")
        # Implement proper alerting here