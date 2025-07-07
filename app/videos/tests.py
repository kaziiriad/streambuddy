from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.response import Response
from .models import Video
from unittest.mock import patch, MagicMock
import os
from django.conf import settings

User = get_user_model()

@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'test_media'))
class VideoAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='otherpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        self.video = Video.objects.create(
            user=self.user,
            title='test-video',
            display_title='Test Video',
            original_filename='test.mp4'
        )

    def test_video_list(self):
        response = self.client.get('/api/videos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'test-video')

    def test_video_detail(self):
        response = self.client.get(f'/api/videos/{self.video.title}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'test-video')

    def test_video_delete(self):
        response = self.client.delete(f'/api/videos/{self.video.title}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Video.objects.count(), 0)

    @patch('videos.api.streaming.StreamingService')
    def test_get_mpd_x_accel_redirect(self, mock_streaming_service):
        mock_service_instance = mock_streaming_service.return_value
        mock_response = Response(data=b'', status=status.HTTP_200_OK, headers={'X-Accel-Redirect': '/protected_media/dash_output/test-video.mpd'})
        mock_service_instance.serve_mpd.return_value = mock_response
        
        response = self.client.get(f'/api/videos/{self.video.title}/mpd/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('X-Accel-Redirect', response.headers)
        self.assertEqual(response.headers['X-Accel-Redirect'], '/protected_media/dash_output/test-video.mpd')
        self.assertEqual(response.content, b'""')
        mock_service_instance.serve_mpd.assert_called_once_with('test-video')

    @patch('videos.api.streaming.StreamingService')
    def test_get_segment_x_accel_redirect(self, mock_streaming_service):
        mock_service_instance = mock_streaming_service.return_value
        segment_name = 'test-video-segment.m4s'
        mock_response = Response(data=b'', status=status.HTTP_200_OK, headers={'X-Accel-Redirect': f'/protected_media/dash_output/{segment_name}'})
        mock_service_instance.serve_segment.return_value = mock_response

        response = self.client.get(f'/api/videos/{self.video.title}/segments/{segment_name}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('X-Accel-Redirect', response.headers)
        self.assertEqual(response.headers['X-Accel-Redirect'], f'/protected_media/dash_output/{segment_name}')
        self.assertEqual(response.content, b'""')
        mock_service_instance.serve_segment.assert_called_once_with('test-video', segment_name)

    def test_cannot_access_other_user_video(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f'/api/videos/{self.video.title}/mpd/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
