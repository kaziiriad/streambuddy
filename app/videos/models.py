from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class VideoStatus(models.TextChoices):
    UPLOADED = 'UPLOADED', 'Uploaded'
    QUEUED = 'QUEUED', 'Queued'
    PROCESSING = 'PROCESSING', 'Processing'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'

class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    display_title = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    mpd_file = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=VideoStatus.choices,
        default=VideoStatus.UPLOADED
    )
    task_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title
