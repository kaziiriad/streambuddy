import os
import magic
from django.core.exceptions import ValidationError
from django.conf import settings

class VideoValidator:
    """Validator for video files."""
    
    # Allowed video MIME types
    ALLOWED_TYPES = {
        'video/mp4': '.mp4',
        'video/mpeg': '.mpeg',
        'video/quicktime': '.mov',
        'video/x-msvideo': '.avi',
        'video/x-matroska': '.mkv',
        'video/webm': '.webm'
    }
    
    # Maximum file size (10GB by default)
    MAX_SIZE = 10 * 1024 * 1024 * 1024  
    
    @classmethod
    def validate_video_file(cls, file):
        """
        Validates video file type and size.
        Args:
            file: UploadedFile object
        Raises:
            ValidationError: If file is invalid
        """
        # Check file size
        if file.size > cls.MAX_SIZE:
            raise ValidationError(
                f'File size must be no more than {cls.MAX_SIZE/(1024*1024*1024):.1f}GB'
            )
            
        # Check file type using python-magic
        mime = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)  # Reset file pointer
        
        if mime not in cls.ALLOWED_TYPES:
            raise ValidationError(
                f'Unsupported file type {mime}. Allowed types: {", ".join(cls.ALLOWED_TYPES.values())}'
            )

