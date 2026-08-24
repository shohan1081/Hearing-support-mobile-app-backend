from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.authentication import FirebaseAuthentication

from .models import EverydayListeningTip
from .serializers import SkillStrategyAudioSerializer
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


class BaseAudioStrategyView(APIView):
    """
    Base view to retrieve a single audio strategy by slug
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]
    slug_name = None

    def get(self, request, *args, **kwargs):
        seed_default_everyday_listening_tips()
        slug = self.slug_name or kwargs.get('slug')
        tip = EverydayListeningTip.objects.filter(slug=slug, is_active=True).first()

        if not tip:
            return standard_response(
                success=False,
                message=f"Audio strategy for '{slug}' not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = SkillStrategyAudioSerializer(tip, context={'request': request})
        return standard_response(
            success=True,
            message=f"Audio strategy '{tip.title}' retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


# ==========================================
# 1. Everyday Listening Tips Audio Views (5)
# ==========================================
class ReduceBackgroundNoiseAudioView(BaseAudioStrategyView):
    slug_name = 'reduce-background-noise'

class FaceTheSpeakerAudioView(BaseAudioStrategyView):
    slug_name = 'face-the-speaker'

class TakeBreaksAudioView(BaseAudioStrategyView):
    slug_name = 'take-breaks'

class UseVisualCuesAudioView(BaseAudioStrategyView):
    slug_name = 'use-visual-cues'

class AskForRepetitionAudioView(BaseAudioStrategyView):
    slug_name = 'ask-for-repetition'


# ==========================================
# 2. Communication Strategies Audio Views (5)
# ==========================================
class StartConversationAudioView(BaseAudioStrategyView):
    slug_name = 'start-the-conversation'

class ManageGroupConversationsAudioView(BaseAudioStrategyView):
    slug_name = 'manage-group-conversations'

class ImproveUnderstandingAudioView(BaseAudioStrategyView):
    slug_name = 'improve-understanding'

class HandleMisunderstandingsAudioView(BaseAudioStrategyView):
    slug_name = 'handle-misunderstandings'

class BuildStrongerConnectionsAudioView(BaseAudioStrategyView):
    slug_name = 'build-stronger-connections'


# ==========================================
# 3. Building Confidence Audio Views (5)
# ==========================================
class StartSmallAudioView(BaseAudioStrategyView):
    slug_name = 'start-small'

class PrepareBeforeConversationsAudioView(BaseAudioStrategyView):
    slug_name = 'prepare-before-conversations'

class BePatientWithYourselfAudioView(BaseAudioStrategyView):
    slug_name = 'be-patient-with-yourself'

class PracticeEveryDayAudioView(BaseAudioStrategyView):
    slug_name = 'practice-every-day'

class CelebrateProgressAudioView(BaseAudioStrategyView):
    slug_name = 'celebrate-progress'


# ==========================================
# Category List Views
# ==========================================
class EverydayListeningTipsListView(APIView):
    """
    GET /api/skills-strategies/everyday-listening-tips/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_everyday_listening_tips()
        tips = EverydayListeningTip.objects.filter(
            category=EverydayListeningTip.CATEGORY_EVERYDAY_LISTENING,
            is_active=True
        ).order_by('order', 'created_at')
        serializer = SkillStrategyAudioSerializer(tips, many=True, context={'request': request})
        return standard_response(
            success=True,
            message="Everyday Listening Tips retrieved successfully",
            data={
                "section": "Everyday Listening Tips",
                "category_key": EverydayListeningTip.CATEGORY_EVERYDAY_LISTENING,
                "total_count": tips.count(),
                "audios": serializer.data
            },
            status_code=status.HTTP_200_OK
        )


class CommunicationStrategiesListView(APIView):
    """
    GET /api/skills-strategies/communication-strategies/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_everyday_listening_tips()
        tips = EverydayListeningTip.objects.filter(
            category=EverydayListeningTip.CATEGORY_COMMUNICATION_STRATEGIES,
            is_active=True
        ).order_by('order', 'created_at')
        serializer = SkillStrategyAudioSerializer(tips, many=True, context={'request': request})
        return standard_response(
            success=True,
            message="Communication Strategies retrieved successfully",
            data={
                "section": "Communication Strategies",
                "category_key": EverydayListeningTip.CATEGORY_COMMUNICATION_STRATEGIES,
                "total_count": tips.count(),
                "audios": serializer.data
            },
            status_code=status.HTTP_200_OK
        )


class BuildingConfidenceListView(APIView):
    """
    GET /api/skills-strategies/building-confidence/
    GET /api/skills-strategies/build-confidence/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_everyday_listening_tips()
        tips = EverydayListeningTip.objects.filter(
            category=EverydayListeningTip.CATEGORY_BUILDING_CONFIDENCE,
            is_active=True
        ).order_by('order', 'created_at')
        serializer = SkillStrategyAudioSerializer(tips, many=True, context={'request': request})
        return standard_response(
            success=True,
            message="Building Confidence strategies retrieved successfully",
            data={
                "section": "Building Confidence",
                "category_key": EverydayListeningTip.CATEGORY_BUILDING_CONFIDENCE,
                "total_count": tips.count(),
                "audios": serializer.data
            },
            status_code=status.HTTP_200_OK
        )


class PracticeAndProgressView(APIView):
    """
    GET /api/skills-strategies/practice-and-progress/
    Section 4: Practice and Progress overview
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        return standard_response(
            success=True,
            message="Practice and Progress section retrieved successfully",
            data={
                "section": "Practice and Progress",
                "has_audio": False,
                "description": (
                    "Track your everyday communication milestones, daily hearing aid wear time consistency, "
                    "and speech clarity rehabilitation progress through your Daily Check-ins and Hearing Health Score."
                ),
                "recommended_actions": [
                    {
                        "title": "Log Daily Wear Time",
                        "description": "Wear hearing aids for target 8+ hours per day",
                        "api_endpoint": "/api/users/wear-time/"
                    },
                    {
                        "title": "Submit Daily Check-in",
                        "description": "Track sound clarity and comfort every day",
                        "api_endpoint": "/api/users/checkin/"
                    },
                    {
                        "title": "View Hearing Health Score",
                        "description": "Monitor objective improvement progress score (1-100)",
                        "api_endpoint": "/api/users/hearing-score/"
                    }
                ]
            },
            status_code=status.HTTP_200_OK
        )


class SkillsStrategiesOverviewView(APIView):
    """
    Main Overview Endpoint
    GET /api/skills-strategies/
    GET /api/skills-strategies/overview/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_everyday_listening_tips()

        cat1_tips = EverydayListeningTip.objects.filter(
            category=EverydayListeningTip.CATEGORY_EVERYDAY_LISTENING,
            is_active=True
        ).order_by('order')
        cat2_tips = EverydayListeningTip.objects.filter(
            category=EverydayListeningTip.CATEGORY_COMMUNICATION_STRATEGIES,
            is_active=True
        ).order_by('order')
        cat3_tips = EverydayListeningTip.objects.filter(
            category=EverydayListeningTip.CATEGORY_BUILDING_CONFIDENCE,
            is_active=True
        ).order_by('order')

        serializer_context = {'request': request}

        return standard_response(
            success=True,
            message="Skills & Strategies all sections retrieved successfully",
            data={
                "main_section": "Skills & Strategies",
                "sections": [
                    {
                        "id": 1,
                        "title": "Everyday Listening Tips",
                        "slug": "everyday-listening-tips",
                        "has_audio": True,
                        "audio_count": cat1_tips.count(),
                        "endpoint": "/api/skills-strategies/everyday-listening-tips/",
                        "items": SkillStrategyAudioSerializer(cat1_tips, many=True, context=serializer_context).data
                    },
                    {
                        "id": 2,
                        "title": "Communication Strategies",
                        "slug": "communication-strategies",
                        "has_audio": True,
                        "audio_count": cat2_tips.count(),
                        "endpoint": "/api/skills-strategies/communication-strategies/",
                        "items": SkillStrategyAudioSerializer(cat2_tips, many=True, context=serializer_context).data
                    },
                    {
                        "id": 3,
                        "title": "Building Confidence",
                        "slug": "building-confidence",
                        "has_audio": True,
                        "audio_count": cat3_tips.count(),
                        "endpoint": "/api/skills-strategies/building-confidence/",
                        "items": SkillStrategyAudioSerializer(cat3_tips, many=True, context=serializer_context).data
                    },
                    {
                        "id": 4,
                        "title": "Practice and Progress",
                        "slug": "practice-and-progress",
                        "has_audio": False,
                        "audio_count": 0,
                        "endpoint": "/api/skills-strategies/practice-and-progress/",
                        "items": []
                    }
                ]
            },
            status_code=status.HTTP_200_OK
        )


class EverydayListeningTipDetailView(BaseAudioStrategyView):
    """
    Lookup by ID or slug:
    GET /api/skills-strategies/audio/<lookup>/
    """
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
                message=f"Audio strategy '{lookup}' not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = SkillStrategyAudioSerializer(tip, context={'request': request})
        return standard_response(
            success=True,
            message=f"Audio strategy '{tip.title}' retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


# Backward-compatibility alias
EverydayListeningTipListView = EverydayListeningTipsListView