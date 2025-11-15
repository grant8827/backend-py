"""
Health check and utility views
"""

from django.http import JsonResponse
from django.conf import settings
import time


def health_check(request):
    """Health check endpoint for load balancers and monitoring"""
    return JsonResponse({
        'success': True,
        'service': 'OneStopRadio API',
        'version': '1.0.0',
        'status': 'healthy',
        'timestamp': time.time(),
        'debug': settings.DEBUG,
        'database': 'connected'  # Could add actual DB health check
    })