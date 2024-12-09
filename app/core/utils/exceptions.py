from rest_framework.exceptions import APIException
from rest_framework import status

class VideoProcessingError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'An error occurred while processing the video.'
    default_code = 'video_processing_error'

class StorageError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'An error occurred while storing the file.'
    default_code = 'storage_error'

class VideoNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'The requested video was not found.'
    default_code = 'video_not_found'

class InvalidVideoError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'The video file is invalid or corrupted.'
    default_code = 'invalid_video'

class DuplicateTitleError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'A video with this title already exists.'
    default_code = 'duplicate_title'

# Usage example in your views:
"""
from .utils.validators import VideoValidator
from .utils.file_handlers import FileManager
from .utils.video_helpers import VideoInfo
from .utils.exceptions import VideoProcessingError

class VideoUploadAPIView(APIView):
    def post(self, request):
        try:
            # Validate video file
            VideoValidator.validate_video_file(request.FILES['file'])
            
            # Get safe filename
            filename = FileManager.safe_filename(request.FILES['file'].name)
            
            # Ensure unique filename
            filename = FileManager.get_available_filename(settings.MEDIA_ROOT, filename)
            
            # Get video metadata
            metadata = VideoInfo.get_video_metadata(file_path)
            
            # Process video...
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
        except VideoProcessingError as e:
            return Response({'error': str(e)}, status=500)
"""