from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.http import Http404

from ..models import Video
from ..services.streaming import StreamingService
from ..services.video_processor import VideoProcessor
from ..serializers.video import VideoMetadataSerializer

from streambuddy_common.throttles import VideoUploadRateThrottle, StreamingRateThrottle, BurstRateThrottle


class VideoListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        videos = Video.objects.filter(user=request.user)
        serializer = VideoMetadataSerializer(videos, many=True)
        return Response(serializer.data)


class VideoStreamingAPIView(APIView):
    throttle_classes = [StreamingRateThrottle]
    permission_classes = [IsAuthenticated]

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
        try:
            Video.objects.get(title=title, user=request.user)
            return self.streaming_service.serve_mpd(title)
        except Video.DoesNotExist:
            return Response(
                {'error': 'Video not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
class VideoSegmentAPIView(APIView):
    throttle_classes = [StreamingRateThrottle]
    permission_classes = [IsAuthenticated]

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
        try:
            Video.objects.get(title=title, user=request.user)
            return self.streaming_service.serve_segment(title, segment)
        except Video.DoesNotExist:
            return Response(
                {'error': 'Video not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class VideoInfoAPIView(APIView):
    throttle_classes = [BurstRateThrottle]
    permission_classes = [IsAuthenticated]

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
        try:
            video = Video.objects.get(title=title, user=request.user)
            serializer = VideoMetadataSerializer(video)
            return Response(serializer.data)
        except Video.DoesNotExist:
            return Response(
                {'error': 'Video not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, title):
        try:
            video = Video.objects.get(title=title, user=request.user)
            video.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Video.DoesNotExist:
            return Response(
                {'error': 'Video not found'},
                status=status.HTTP_404_NOT_FOUND
            )
