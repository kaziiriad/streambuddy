from rest_framework import serializers
from ..models import Video
import os
from django.conf import settings

class VideoUploadSerializer(serializers.Serializer):

    title = serializers.CharField(max_length=255)
    file = serializers.FileField()

    def validate_title(self, value):
        """Validate title is unique in metadata directory."""
        metadata_path = os.path.join(settings.MEDIA_ROOT, 'metadata', f"{value}.json")
        if os.path.exists(metadata_path):
            raise serializers.ValidationError("A video with this title already exists")
        return value

class VideoMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('id', 'title', 'display_title', 'original_filename', 'uploaded_at', 'processed', 'mpd_file')




