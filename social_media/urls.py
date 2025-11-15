from django.urls import path
from django.http import JsonResponse

def social_keys(request):
    return JsonResponse({})  # Placeholder

urlpatterns = [
    path('keys/', social_keys, name='social_keys'),
]