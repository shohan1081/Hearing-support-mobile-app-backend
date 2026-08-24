from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.authentication import FirebaseAuthentication

from .models import AIChatSession, AIChatMessage, QuickPromptSuggestion
from .serializers import (
    AIChatMessageSerializer,
    AIChatSessionSerializer,
    AIChatSessionDetailSerializer,
    SendAIChatMessageInputSerializer,
    QuickPromptSuggestionSerializer,
)
from .services import generate_ai_chat_response, build_user_hearing_context


def standard_response(success=True, message="", data=None, errors=None, status_code=status.HTTP_200_OK):
    """
    Standard JSON response format
    """
    res = {
        'success': success,
        'message': message,
    }
    if data is not None:
        res['data'] = data
    if errors is not None:
        res['errors'] = errors
    return Response(res, status=status_code)


def seed_default_quick_prompts_if_needed():
    """
    Seed initial set of hearing improvement quick prompt chips if table is empty
    """
    if QuickPromptSuggestion.objects.exists():
        return

    defaults = [
        {
            "title": "Improve Hearing Score",
            "prompt_text": "How can I improve my hearing score?",
            "category": QuickPromptSuggestion.CATEGORY_HEARING_SCORE,
            "icon": "trending_up",
            "order": 1,
        },
        {
            "title": "Noisy Environments",
            "prompt_text": "What exercises help with noisy environments and restaurants?",
            "category": QuickPromptSuggestion.CATEGORY_NOISY_ENVIRONMENTS,
            "icon": "volume_up",
            "order": 2,
        },
        {
            "title": "Struggling with Tinnitus",
            "prompt_text": "I'm struggling with tinnitus today. What should I do for relief?",
            "category": QuickPromptSuggestion.CATEGORY_TINNITUS,
            "icon": "hearing",
            "order": 3,
        },
        {
            "title": "My Progress & Wear Time",
            "prompt_text": "Tell me about my progress and daily wear time.",
            "category": QuickPromptSuggestion.CATEGORY_PROGRESS,
            "icon": "insights",
            "order": 4,
        },
        {
            "title": "Clean & Maintain Device",
            "prompt_text": "How do I clean my hearing aid and change the wax filter?",
            "category": QuickPromptSuggestion.CATEGORY_DEVICE_CARE,
            "icon": "cleaning_services",
            "order": 5,
        },
        {
            "title": "Bluetooth Pairing Help",
            "prompt_text": "How do I pair my hearing aids to my phone via Bluetooth?",
            "category": QuickPromptSuggestion.CATEGORY_DEVICE_CARE,
            "icon": "bluetooth",
            "order": 6,
        },
    ]

    for item in defaults:
        QuickPromptSuggestion.objects.create(**item)


class AIChatView(APIView):
    """
    Main AI Hearing Assistant Chat Endpoint
    
    POST /api/chatbot/chat/
    POST /api/chatbot/message/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def post(self, request):
        input_serializer = SendAIChatMessageInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return standard_response(
                success=False,
                message="Invalid message input",
                errors=input_serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        message_text = input_serializer.validated_data['message']
        session_id = input_serializer.validated_data.get('session_id')

        try:
            chat_result = generate_ai_chat_response(
                user=request.user,
                message_text=message_text,
                session_id=session_id
            )
            return standard_response(
                success=True,
                message="AI response generated successfully.",
                data=chat_result,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return standard_response(
                success=False,
                message="Failed to generate AI response",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuickPromptSuggestionsView(APIView):
    """
    Fetch suggested quick questions to display in chatbot UI
    
    GET /api/chatbot/suggestions/
    GET /api/chatbot/quick-prompts/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_quick_prompts_if_needed()
        prompts = QuickPromptSuggestion.objects.filter(is_active=True).order_by('order', 'created_at')
        serializer = QuickPromptSuggestionSerializer(prompts, many=True)
        return standard_response(
            success=True,
            message="Quick prompt suggestions retrieved successfully.",
            data={
                "total_count": prompts.count(),
                "suggestions": serializer.data
            },
            status_code=status.HTTP_200_OK
        )


class AIChatSessionListView(APIView):
    """
    List user's AI chat conversation sessions
    
    GET /api/chatbot/sessions/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        sessions = AIChatSession.objects.filter(user=request.user).order_by('-last_interaction_at')
        serializer = AIChatSessionSerializer(sessions, many=True)
        return standard_response(
            success=True,
            message="AI chat sessions retrieved successfully.",
            data={
                "total_count": sessions.count(),
                "sessions": serializer.data
            },
            status_code=status.HTTP_200_OK
        )


class AIChatSessionDetailView(APIView):
    """
    Retrieve full chat history or delete a chat session
    
    GET /api/chatbot/sessions/<uuid:session_id>/
    DELETE /api/chatbot/sessions/<uuid:session_id>/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request, session_id):
        session = AIChatSession.objects.filter(session_id=session_id, user=request.user).first()
        if not session:
            return standard_response(
                success=False,
                message="AI chat session not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = AIChatSessionDetailSerializer(session)
        return standard_response(
            success=True,
            message="AI chat session retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def delete(self, request, session_id):
        session = AIChatSession.objects.filter(session_id=session_id, user=request.user).first()
        if not session:
            return standard_response(
                success=False,
                message="AI chat session not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        session.delete()
        return standard_response(
            success=True,
            message="AI chat session deleted successfully.",
            status_code=status.HTTP_200_OK
        )


class ClearAIChatSessionView(APIView):
    """
    Clear all chat messages or archive active sessions
    
    POST /api/chatbot/clear/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def post(self, request):
        session_id = request.data.get('session_id')
        if session_id:
            session = AIChatSession.objects.filter(session_id=session_id, user=request.user).first()
            if session:
                session.messages.all().delete()
                session.last_interaction_at = timezone.now()
                session.save()
                return standard_response(
                    success=True,
                    message="Chat session history cleared successfully.",
                    status_code=status.HTTP_200_OK
                )

        # Clear all user's sessions if no specific session_id given
        AIChatSession.objects.filter(user=request.user).delete()
        return standard_response(
            success=True,
            message="All AI chat history cleared successfully.",
            status_code=status.HTTP_200_OK
        )