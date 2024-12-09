from django.conf import settings
from django.http import FileResponse, Http404
import os
import logging

class StreamingService:
    def __init__(self, output_dir=None):
        self.output_dir = os.path.join(settings.MEDIA_ROOT, 'dash_output')
        os.makedirs(self.output_dir, exist_ok=True)


    def serve_mpd(self, title):
        """Serve MPD file."""
        try:
            file_path = os.path.join(self.output_dir, f"{title}.mpd")
            response = FileResponse(
                open(file_path, 'rb'),
                content_type='application/dash+xml'
            )
            response['Access-Control-Allow-Origin'] = '*'  # For CORS if needed
            return response
        except FileNotFoundError:
            raise Http404("MPD File Not Found")

    def serve_segment(self, title, segment):
        """Serve video segment."""
        try:
            # The segment parameter will be something like "init.mp4" or "chunk-stream0-00001.m4s"
            file_path = os.path.join(self.output_dir, segment)
            
            # Validate that the requested segment belongs to this video
            if not self._is_valid_segment(title, segment):
                raise Http404("Invalid segment requested")
                
            response = FileResponse(
                open(file_path, 'rb'),
                content_type='video/mp4'  # Use appropriate content type for segments
            )
            response['Access-Control-Allow-Origin'] = '*'  # For CORS if needed
            return response
        except FileNotFoundError:
            raise Http404("Segment Not Found")

    def _is_valid_segment(self, title, segment):
        """Validate that the segment belongs to the specified video."""
        # Basic validation - you might want to make this more robust
        valid_extensions = ('.mp4', '.m4s')
        if not segment.endswith(valid_extensions):
            return False
            
        # If using FFmpeg's default naming pattern, segments will start with "init" or "chunk"
        if not (segment.startswith('init') or segment.startswith('chunk')):
            return False
            
        # Additional validation could be added here
        return True
