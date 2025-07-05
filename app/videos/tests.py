from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Video

User = get_user_model()


class VideoAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword'
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