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

from datetime import datetime

from celery.result import AsyncResult

class VideoProcessingStatusView(APIView):
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
            title = serializer.validated_data['title']
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
                'title': title,
                'original_filename': file.name,
                'uploaded_at': str(datetime.now()),
                'processed': False,
                'status': 'uploaded'
            }
            storage.save_metadata(title, metadata)

            # Save the file temporarily
            temp_path = storage.save_temp_upload(file, title)

            # Start processing task
            task = process_video_task.delay(temp_path, title)

            # Update metadata with task ID
            metadata.update({
                'status': 'queued',
                'task_id': task.id
            })
            storage.save_metadata(title, metadata)

            return Response({
                'message': 'Video upload successful, processing started',
                'title': title,
                'task_id': task.id,
                'status': 'queued'
            }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
