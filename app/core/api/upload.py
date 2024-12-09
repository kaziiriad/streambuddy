from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from ..serializers.video import VideoUploadSerializer, VideoMetadataSerializer
from ..services.video_processor import VideoProcessor
from ..services.storage import StorageService

from ..utils.exceptions import (
    VideoProcessingError,
    StorageError,
    VideoNotFoundError,
    InvalidVideoError,
    DuplicateTitleError
)


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
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            title = serializer.validated_data['title']
            file = serializer.validated_data['file']

            # Process the upload using the single method that handles everything
            video_info = self.video_processor.process_upload(file, title)
            
            # Validate the video info with the serializer
            metadata_serializer = VideoMetadataSerializer(data=video_info)
            if not metadata_serializer.is_valid():
                return Response(
                    metadata_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                metadata_serializer.data,
                status=status.HTTP_201_CREATED
            )

        except InvalidVideoError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DuplicateTitleError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_409_CONFLICT
            )
        except (VideoProcessingError, StorageError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            # Log the actual error for debugging
            import logging
            logging.error(f"Unexpected error in video upload: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred while processing the video"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
