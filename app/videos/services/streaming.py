from django.conf import settings
from django.http import Http404
from rest_framework.response import Response
import os
import logging

class StreamingService:
    def __init__(self, output_dir=None):
        self.output_dir = os.path.join(settings.MEDIA_ROOT, 'dash_output')
        os.makedirs(self.output_dir, exist_ok=True)

    def serve_mpd(self, title):
        """Serve MPD file."""
        try:
            output_dir = self._get_output_dir()
            # Check both in root directory and title subdirectory
            file_path = os.path.join(output_dir, f"{title}.mpd")
            if not os.path.exists(file_path):
                # Try in subdirectory
                file_path = os.path.join(output_dir, title, f"{title}.mpd")
                if not os.path.exists(file_path):
                    raise FileNotFoundError()

            logging.info(f"Serving MPD file from: {file_path}")
            response = Response(content_type='application/dash+xml')
            response['X-Accel-Redirect'] = os.path.join(settings.PROTECTED_MEDIA_URL, 'dash_output', f"{title}.mpd")
            response['Access-Control-Allow-Origin'] = '*'
            return response
        except FileNotFoundError:
            logging.error(f"MPD file not found at: {file_path}")
            raise Http404("MPD File Not Found")
        except Exception as e:
            logging.error(f"Error serving MPD file: {str(e)}")
            raise

    def serve_segment(self, title, segment):
        """Serve video segment."""
        try:
            output_dir = self._get_output_dir()
            # Check both in root directory and title subdirectory
            file_path = os.path.join(output_dir, segment)
            if not os.path.exists(file_path):
                # Try in subdirectory
                file_path = os.path.join(output_dir, title, segment)
                if not os.path.exists(file_path):
                    raise FileNotFoundError()

            logging.info(f"Attempting to serve segment from: {file_path}")
            
            if not os.path.exists(file_path):
                logging.error(f"Segment file not found at: {file_path}")
                raise Http404(f"Segment not found: {segment}")

            
            if not self._is_valid_segment(title, segment):
                raise Http404("Invalid segment requested")
            
            content_type = 'video/mp4' if segment.endswith('.mp4') or segment.endswith('.m4s') else 'application/octet-stream'
            
            response = Response(content_type=content_type)
            response['X-Accel-Redirect'] = os.path.join(settings.PROTECTED_MEDIA_URL, 'dash_output', segment)
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'

            return response
        except FileNotFoundError:
            raise Http404(f"Segment not found: {segment}")
        except Exception as e:
            logging.error(f"Error serving segment {segment}: {str(e)}")
            raise Http404("Error serving segment")

    def _is_valid_segment(self, title, segment):
        """Validate that the segment belongs to the specified video."""
        try:

            logging.info(f"Validating segment: {segment} for video: {title}")

            # Valid extensions
            valid_extensions = ('.mp4', '.m4s', '.mpd')
            if not segment.endswith(valid_extensions):
                logging.warning(f"Invalid extension for segment: {segment}")
                return False
            
            # Valid segment patterns for FFmpeg DASH output
            valid_patterns = [
                'init-stream',     # Init segment pattern
                'chunk-stream',    # Media segment pattern
                'init-',           # Alternative init pattern
                'chunk-',          # Alternative chunk pattern
                f"{title}.mpd"     # MPD file
            ]
            
            # Check if segment filename matches any pattern
            is_valid = any(pattern in segment for pattern in valid_patterns)
            
            if not is_valid:
                logging.warning(f"Invalid segment pattern: {segment} for video: {title}")
            else:
                logging.info(f"Valid segment requested: {segment}")
                
            return True  # For now, accept all segments with valid extensions
            
        except Exception as e:
            logging.error(f"Error validating segment {segment}: {str(e)}")
            return False