from django.urls import path
from .api.upload import VideoUploadAPIView, VideoProcessingStatusView
from .api.streaming import VideoStreamingAPIView, VideoSegmentAPIView, VideoInfoAPIView, VideoListAPIView

urlpatterns = [
    # Remove the 'api/' prefix since it's already included in the main urls.py
    path('videos/', VideoListAPIView.as_view(), name='video_list'),
    path('videos/upload/', VideoUploadAPIView.as_view(), name='video_upload'),
    path('videos/<str:title>/', VideoInfoAPIView.as_view(), name='video_info'),
    # path('videos/<str:title>/progress/', VideoProcessProgressView.as_view(), name='video_progress'),
    path('videos/<str:title>/mpd/', VideoStreamingAPIView.as_view(), name='serve_mpd'),
    path('videos/<str:title>/segments/<str:segment>/', VideoSegmentAPIView.as_view(), name='serve_segments'),
    
    path('tasks/<str:task_id>/', VideoProcessingStatusView.as_view(), name='task_status'),
]