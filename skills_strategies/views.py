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
    Standard standardized API response
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


class BaseStrategyAudioView(APIView):
    """
    Base view to retrieve a specific strategy audio by slug
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]
    slug_name = None

    def get(self, request):
        seed_default_everyday_listening_tips()
        tip = EverydayListeningTip.objects.filter(slug=self.slug_name, is_active=True).first()
        if not tip:
            # Fallback search by normalized title or order
            tip = EverydayListeningTip.objects.filter(is_active=True).first()

        if not tip:
            return standard_response(
                success=False,
                message=f"Strategy audio for '{self.slug_name}' not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = EverydayListeningTipDetailSerializer(tip, context={'request': request})
        return standard_response(
            success=True,
            message=f"Listening strategy '{tip.title}' audio retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class StartConversationAudioView(BaseStrategyAudioView):
    """
    GET /api/skills-strategies/start-the-conversation/
    """
    slug_name = 'start-the-conversation'


class ManageGroupConversationsAudioView(BaseStrategyAudioView):
    """
    GET /api/skills-strategies/manage-group-conversations/
    """
    slug_name = 'manage-group-conversations'


class ImproveUnderstandingAudioView(BaseStrategyAudioView):
    """
    GET /api/skills-strategies/improve-understanding/
    """
    slug_name = 'improve-understanding'


class HandleMisunderstandingsAudioView(BaseStrategyAudioView):
    """
    GET /api/skills-strategies/handle-misunderstandings/
    """
    slug_name = 'handle-misunderstandings'


class BuildStrongerConnectionsAudioView(BaseStrategyAudioView):
    """
    GET /api/skills-strategies/build-stronger-connections/
    """
    slug_name = 'build-stronger-connections'


class EverydayListeningTipListView(APIView):
    """
    GET /api/skills-strategies/
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
            message="Skills & Strategies audio lessons retrieved successfully",
            data={
                "total_count": tips.count(),
                "sections": serializer.data
            },
            status_code=status.HTTP_200_OK
        )


class EverydayListeningTipDetailView(APIView):
    """
    GET /api/skills-strategies/everyday-listening-tips/<slug_or_id>/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request, lookup):
        seed_default_everyday_listening_tips()
        tip = None

        if lookup.isdigit():
            tip = EverydayListeningTip.objects.filter(pk=int(lookup), is_active=True).first()

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
            message=f"Listening tip '{tip.title}' retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )