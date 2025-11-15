"""
Station management views
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Station
from .serializers import StationSerializer, StationCreateUpdateSerializer, StationSocialLinksSerializer


class StationDetailView(generics.RetrieveUpdateAPIView):
    """Get and update user's station"""
    
    serializer_class = StationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        station, created = Station.objects.get_or_create(
            user=self.request.user,
            defaults={
                'name': f"{self.request.user.display_name}'s Radio Station",
                'description': 'My awesome radio station',
                'genre': 'mixed'
            }
        )
        return station
    
    def update(self, request, *args, **kwargs):
        station = self.get_object()
        serializer = StationCreateUpdateSerializer(station, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Station updated successfully',
                'station': StationSerializer(station).data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_social_links(request):
    """Update station social media links"""
    try:
        station = Station.objects.get(user=request.user)
    except Station.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Station not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = StationSocialLinksSerializer(station, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Social links updated successfully',
            'social_links': station.social_links
        })
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_logo(request):
    """Upload station logo"""
    try:
        station = Station.objects.get(user=request.user)
    except Station.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Station not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if 'logo' not in request.FILES:
        return Response({
            'success': False,
            'error': 'No logo file provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    station.logo = request.FILES['logo']
    station.save(update_fields=['logo'])
    
    return Response({
        'success': True,
        'message': 'Logo uploaded successfully',
        'logo_url': station.logo.url if station.logo else None
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_cover(request):
    """Upload station cover image"""
    try:
        station = Station.objects.get(user=request.user)
    except Station.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Station not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if 'cover' not in request.FILES:
        return Response({
            'success': False,
            'error': 'No cover file provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    station.cover_image = request.FILES['cover']
    station.save(update_fields=['cover_image'])
    
    return Response({
        'success': True,
        'message': 'Cover image uploaded successfully',
        'cover_url': station.cover_image.url if station.cover_image else None
    })