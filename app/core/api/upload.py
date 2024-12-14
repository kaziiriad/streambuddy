from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from django.core.exceptions import ValidationError

from ..tasks import process_video_task

from ..serializers.video import VideoUploadSerializer, VideoMetadataSerializer
from ..services.video_processor import VideoProcessor
from ..services.storage import StorageService

from ..utils.exceptions import (
    VideoProcessingError,
    StorageError,
    VideoNotFoundError,
    InvalidVideoError,
    DuplicateTitleError,
)
from ..utils.validators import VideoValidator
from ..utils.filename_utils import sanitize_filename

from ..throttles import VideoUploadRateThrottle, StreamingRateThrottle, BurstRateThrottle


from datetime import datetime

from celery.result import AsyncResult

class VideoProcessingStatusView(APIView):
    throttle_classes = [BurstRateThrottle]
    def get(self, request, task_id):
        task_result = AsyncResult(task_id)
        
        response_data = {
            'task_id': task_id,
            'status': task_result.status,
        }
        
        if task_result.ready():
            if task_result.successful():
                response_data['result'] = task_result.get()
            else:
                response_data['error'] = str(task_result.result)
                
        return Response(response_data)


class VideoUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    throttle_classes = [VideoUploadRateThrottle] 

    def __init__(self):
        self.storage_service = StorageService()
        self.video_processor = VideoProcessor()
        super().__init__()

    @swagger_auto_schema(
        operation_description="Upload a video file",
        request_body=VideoUploadSerializer,
        responses={
            201: openapi.Response(
                description="Video uploaded successfully",
                schema=VideoMetadataSerializer
            ),
            400: openapi.Response(
                description="Invalid input",
                examples={
                    "application/json": {
                        "title": ["This field is required."],
                        "file": ["No file was submitted."]
                    }
                }
            ),
            500: openapi.Response(
                description="Internal server error",
                examples={
                    "application/json": {
                        "error": "Failed to process video"
                    }
                }
            )
        },
        tags=['videos']
    )

    def post(self, request):
        serializer = VideoUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            original_title = serializer.validated_data['title']
            safe_title = sanitize_filename(original_title)
            file = serializer.validated_data['file']

            # Validate the video file
            try:
                VideoValidator.validate_video_file(file)
            except ValidationError as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save initial metadata
            storage = StorageService()
            metadata = {
                'title': safe_title,
                'display_title': original_title,
                'original_filename': file.name,
                'uploaded_at': str(datetime.now()),
                'processed': False,
                'status': 'uploaded'
            }
            storage.save_metadata(safe_title, metadata)

            # Save the file temporarily
            temp_path = storage.save_temp_upload(file, safe_title)

            # Start processing task
            task = process_video_task.delay(temp_path, safe_title)

            # Update metadata with task ID
            metadata.update({
                'status': 'queued',
                'task_id': task.id
            })
            storage.save_metadata(safe_title, metadata)

            return Response({
                'message': 'Video upload successful, processing started',
                'title': safe_title,
                'display_title': original_title,
                'task_id': task.id,
                'status': 'queued'
            }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VideoProcessProgressView(APIView):
    @swagger_auto_schema(
        operation_description="Get video processing progress",
        responses={
            200: openapi.Response(
                description="Processing progress",
                examples={
                    "application/json": {
                        "status": "processing",
                        "progress": 45.5,
                        "current_resolution": "720p",
                        "resolution_progress": "2/3",
                        "estimated_time_remaining": 120
                    }
                }
            )
        }
    )
    def get(self, request, title):
        storage_service = StorageService()
        metadata = storage_service.get_metadata(title)
        
        if not metadata:
            return Response(
                {"error": "Video not found"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        progress_data = {
            "status": metadata.get("status", "unknown"),
            "progress": metadata.get("processing_progress", 0),
            "current_resolution": metadata.get("current_resolution"),
            "resolution_progress": metadata.get("resolution_progress"),
            "estimated_time_remaining": metadata.get("estimated_time_remaining")
        }
        
        return Response(progress_data)