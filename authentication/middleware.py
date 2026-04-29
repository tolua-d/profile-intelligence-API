"""
Middleware for rate limiting and request logging
"""
import logging
import time
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Middleware to log all API requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        # Log request details
        logger.info(
            f"API Request: {request.method} {request.path} | "
            f"User: {request.user if request.user.is_authenticated else 'Anonymous'} | "
            f"IP: {self._get_client_ip(request)}"
        )
        
        response = self.get_response(request)
        
        # Log response
        duration = time.time() - start_time
        logger.info(
            f"API Response: {request.method} {request.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.2f}s"
        )
        
        return response
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitMiddleware:
    """Middleware to implement rate limiting"""
    
    RATE_LIMIT_REQUESTS = 100  # requests
    RATE_LIMIT_PERIOD = 3600  # seconds (1 hour)
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if not settings.RATELIMIT_ENABLE:
            return self.get_response(request)
        
        client_ip = self._get_client_ip(request)
        cache_key = f"rate_limit:{client_ip}"
        
        # Get current request count
        request_count = cache.get(cache_key, 0)
        
        if request_count >= self.RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JsonResponse(
                {"error": "Rate limit exceeded. Please try again later."},
                status=429
            )
        
        # Increment request count
        cache.set(cache_key, request_count + 1, self.RATE_LIMIT_PERIOD)
        
        response = self.get_response(request)
        
        # Add rate limit headers
        response['X-RateLimit-Limit'] = str(self.RATE_LIMIT_REQUESTS)
        response['X-RateLimit-Remaining'] = str(
            self.RATE_LIMIT_REQUESTS - request_count - 1
        )
        response['X-RateLimit-Reset'] = str(
            int(time.time()) + self.RATE_LIMIT_PERIOD
        )
        
        return response
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
