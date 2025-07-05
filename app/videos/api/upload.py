from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from django.core.exceptions import ValidationError

from ..models import Video, VideoStatus
from ..tasks import process_video_task

from ..serializers.video import VideoUploadSerializer, VideoMetadataSerializer
from ..services.video_processor import VideoProcessor
from ..services.storage import StorageService

from streambuddy_common.exceptions import (
    VideoProcessingError,
    StorageError,
    VideoNotFoundError,
    InvalidVideoError,
    DuplicateTitleError,
)
from streambuddy_common.utils.validators import VideoValidator
from streambuddy_common.utils.filename_utils import sanitize_filename

from streambuddy_common.throttles import VideoUploadRateThrottle, StreamingRateThrottle, BurstRateThrottle


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
    permission_classes = [IsAuthenticated] 

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
            video = Video.objects.create(
                user=request.user,
                title=safe_title,
                display_title=original_title,
                original_filename=file.name,
            )

            # Save the file temporarily
            storage = StorageService()
            temp_path = storage.save_temp_upload(file, safe_title)

            # Start processing task
            task = process_video_task.delay(temp_path, safe_title, video.id)

            # Update metadata with task ID
            video.task_id = task.id
            video.status = VideoStatus.QUEUED
            video.save()

            return Response({
                'message': 'Video upload successful, processing started',
                'title': safe_title,
                'display_title': original_title,
                'task_id': task.id,
                'status': VideoStatus.QUEUED
            }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VideoProcessProgressView(APIView):
    permission_classes = [IsAuthenticated]

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
        try:
            video = Video.objects.get(title=title, user=request.user)
            progress_data = {
                "status": video.status,
                "progress": 0,  # This needs to be implemented
                "current_resolution": None, # This needs to be implemented
                "resolution_progress": None, # This needs to be implemented
                "estimated_time_remaining": None # This needs to be implemented
            }
            return Response(progress_data)
        except Video.DoesNotExist:
            return Response(
                {"error": "Video not found"},
                status=status.HTTP_404_NOT_FOUND
            )