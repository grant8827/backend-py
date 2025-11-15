from django.urls import path
from django.http import JsonResponse

def stream_history(request):
    return JsonResponse([])  # Placeholder

urlpatterns = [
    path('history/', stream_history, name='stream_history'),
]