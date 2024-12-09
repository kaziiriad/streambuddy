from django.urls import path
from .api.upload import VideoUploadAPIView
from .api.streaming import VideoStreamingAPIView, VideoSegmentAPIView, VideoInfoAPIView
from .views import VideoPlayerView

urlpatterns = [
    # Remove the 'api/' prefix since it's already included in the main urls.py
    path('videos/', VideoUploadAPIView.as_view(), name='video_upload'),
    path('videos/<str:title>/', VideoInfoAPIView.as_view(), name='video_info'),
    path('videos/<str:title>/mpd/', VideoStreamingAPIView.as_view(), name='serve_mpd'),
    path('videos/<str:title>/segments/<str:segment>/', VideoSegmentAPIView.as_view(), name='serve_segments'),
    
]