class RateLimitHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add rate limit headers if available
        if hasattr(request, 'throttle_status'):
            response['X-RateLimit-Limit'] = request.throttle_status.get('num_requests', '')
            response['X-RateLimit-Remaining'] = request.throttle_status.get('remaining_requests', '')
            response['X-RateLimit-Reset'] = request.throttle_status.get('duration', '')
            
        return response
