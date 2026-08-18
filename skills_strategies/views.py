from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.authentication import FirebaseAuthentication

from .models import EverydayListeningTip
from .serializers import (
    EverydayListeningTipListSerializer,
    EverydayListeningTipDetailSerializer,
)
from .utils import seed_default_everyday_listening_tips


def standard_response(success=True, message="", data=None, errors=None, status_code=status.HTTP_200_OK):
    """
    Create standardized API response for consistency across the application
    """
    response_data = {
        'success': success,
        'message': message,
    }
    if data is not None:
        response_data['data'] = data
    if errors is not None:
        response_data['errors'] = errors
    return Response(response_data, status=status_code)


class EverydayListeningTipListView(APIView):
    """
    API endpoint to list all Everyday Listening Tips (Reduce Background Noise, Face Speaker, etc.)
    
    GET /api/skills-strategies/everyday-listening-tips/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_everyday_listening_tips()
        tips = EverydayListeningTip.objects.filter(is_active=True).order_by('order', 'created_at')
        serializer = EverydayListeningTipListSerializer(tips, many=True, context={'request': request})
        return standard_response(
            success=True,
            message="Everyday listening tips retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class EverydayListeningTipDetailView(APIView):
    """
    API endpoint to get detail & audio stream URL for a specific listening tip by slug or ID
    
    GET /api/skills-strategies/everyday-listening-tips/<slug_or_id>/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request, lookup):
        seed_default_everyday_listening_tips()
        tip = None

        # Try lookup by integer ID
        if lookup.isdigit():
            tip = EverydayListeningTip.objects.filter(pk=int(lookup), is_active=True).first()

        # Fallback to lookup by slug
        if not tip:
            tip = EverydayListeningTip.objects.filter(slug=lookup, is_active=True).first()

        if not tip:
            return standard_response(
                success=False,
                message=f"Listening tip '{lookup}' not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = EverydayListeningTipDetailSerializer(tip, context={'request': request})
        return standard_response(
            success=True,
            message=f"Listening tip '{tip.title}' details retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
