from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled

class VideoUploadRateThrottle(UserRateThrottle):
    rate = '10/day'
    scope = 'uploads'

class StreamingRateThrottle(AnonRateThrottle):
    rate = '1000/hour'
    scope = 'streaming'

class BurstRateThrottle(AnonRateThrottle):
    rate = '60/minute'
    scope = 'burst'

def custom_throttle_handler(exc, context):
    """Custom throttle exception handler."""
    response = exception_handler(exc, context)
    
    if isinstance(exc, Throttled):
        custom_response_data = {
            'error': 'rate_limit_exceeded',
            'message': 'Too many requests. Please try again later.',
            'wait_seconds': exc.wait,
            'detail': {
                'available_in': f'{exc.wait} seconds',
                'throttle_type': context['view'].get_throttles()[0].scope if context.get('view') else 'unknown'
            }
        }
        response.data = custom_response_data
    
    return response