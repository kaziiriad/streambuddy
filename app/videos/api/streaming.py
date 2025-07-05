from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.http import FileResponse, Http404

from ..services.streaming import StreamingService
from ..services.video_processor import VideoProcessor
from ..serializers.video import VideoMetadataSerializer

from streambuddy_common.throttles import VideoUploadRateThrottle, StreamingRateThrottle, BurstRateThrottle


class VideoStreamingAPIView(APIView):

    throttle_classes = [StreamingRateThrottle]

    def __init__(self):
        self.streaming_service = StreamingService()
        super().__init__()

    @swagger_auto_schema(
        operation_description="Get the MPD file for DASH streaming",
        manual_parameters=[
            openapi.Parameter(
                'title',
                openapi.IN_PATH,
                description="Video title",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="MPD file",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            404: "Video not found"
        },
        tags=['streaming']
    )


    def get(self, request, title):
        return self.streaming_service.serve_mpd(title)
    
class VideoSegmentAPIView(APIView):

    throttle_classes = [StreamingRateThrottle]

    def __init__(self):
        self.streaming_service = StreamingService()
        super().__init__()
    
    @swagger_auto_schema(
        operation_description="Get a video segment",
        manual_parameters=[
            openapi.Parameter(
                'title',
                openapi.IN_PATH,
                description="Video title",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'segment',
                openapi.IN_PATH,
                description="Segment filename",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Video segment file",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            404: "Segment not found"
        },
        tags=['streaming']
    )

    def get(self, request, title, segment):
        return self.streaming_service.serve_segment(title, segment)

class VideoInfoAPIView(APIView):

    throttle_classes = [BurstRateThrottle]

    def __init__(self):
        self.video_processor = VideoProcessor()
        super().__init__()

    @swagger_auto_schema(
        operation_description="Get video information",
        manual_parameters=[
            openapi.Parameter(
                'title',
                openapi.IN_PATH,
                description="Video title",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: VideoMetadataSerializer,
            404: "Video not found"
        },
        tags=['videos']
    )

    def get(self, request, title):
        video_info = self.video_processor.get_video_info(title)
        if not video_info:
            return Response(
                {'error': 'Video not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = VideoMetadataSerializer(video_info)
        return Response(serializer.data)
