from streambuddy.celery import app
from celery import shared_task
from .services.video_processor import VideoProcessor
from .services.storage import StorageService
from .models import Video, VideoStatus
from streambuddy_common.utils.progress_tracker import FFmpegProgress
from datetime import datetime
import logging
from celery import Task
import os


class VideoProcessingTask(Task):
    name = 'process_video'

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        video_id = args[2] if len(args) > 2 else None
        if video_id:
            try:
                video = Video.objects.get(id=video_id)
                video.status = VideoStatus.FAILED
                video.save()
            except Video.DoesNotExist:
                logging.error(f"Video with id {video_id} not found on failure.")
            except Exception as e:
                logging.error(f"Failed to update video status on failure: {str(e)}")

@shared_task(base=VideoProcessingTask, bind=True)
def process_video_task(self, file_path, title, video_id):
    """Celery task for processing video files with progress tracking."""
    processor = VideoProcessor()
    storage = StorageService()

    try:
        video = Video.objects.get(id=video_id)
        video.status = VideoStatus.PROCESSING
        video.task_id = self.request.id
        video.save()

        # Set lower nice value for FFmpeg process
        os.nice(10)

        # Process video with progress tracking
        result = processor.process_to_dash(file_path, title)

        if result.returncode != 0:
            raise Exception(f"FFMPEG error: {result.stderr}")

        # Update completion metadata
        video.processed = True
        video.status = VideoStatus.COMPLETED
        video.mpd_file = f"{title}.mpd"
        video.save()

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

    except Video.DoesNotExist:
        logging.error(f"Video with id {video_id} not found.")
        raise
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