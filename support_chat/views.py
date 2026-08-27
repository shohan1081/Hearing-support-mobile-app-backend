from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.authentication import CustomJWTAuthentication, FirebaseAuthentication

from .models import SupportConversation, SupportMessage
from .serializers import (
    SupportMessageSerializer,
    SupportConversationDetailSerializer,
    SendMessageInputSerializer,
)
from .utils import (
    get_or_create_user_support_conversation,
    seed_default_support_chat_sample,
    send_admin_new_message_notification,
)


def standard_response(success=True, message="", data=None, errors=None, status_code=status.HTTP_200_OK):
    """
    Standard standardized API response for consistency across application
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


class UserConversationView(APIView):
    """
    API endpoint to retrieve the full chat history thread for the authenticated user
    
    GET /api/support-chat/messages/
    GET /api/support-chat/conversation/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        conversation = seed_default_support_chat_sample(request.user)

        serializer = SupportConversationDetailSerializer(conversation, context={'request': request})
        return standard_response(
            success=True,
            message="Full support chat history retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class SendMessageView(APIView):
    """
    API endpoint for mobile user to post a message with optional picture/video/audio/file to Care Team
    
    POST /api/support-chat/send/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication, FirebaseAuthentication]

    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            return standard_response(
                success=False,
                message="Authentication required. Please provide a valid Bearer token in the Authorization header.",
                errors={"detail": "Authentication credentials were not provided."},
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        serializer = SendMessageInputSerializer(data=request.data)
        if not serializer.is_valid():
            return standard_response(
                success=False,
                message="Validation failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data
        subject = validated_data.get('subject', 'Care Team Support Chat')
        conversation = get_or_create_user_support_conversation(request.user, subject=subject)

        # Detect attachment type automatically from file extension
        attachment_file = validated_data.get('attachment')
        attachment_type = validated_data.get('attachment_type', SupportMessage.TYPE_TEXT)
        if attachment_file and attachment_type == SupportMessage.TYPE_TEXT:
            fname = attachment_file.name.lower()
            if fname.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg')):
                attachment_type = SupportMessage.TYPE_IMAGE
            elif fname.endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.3gp', '.m4v')):
                attachment_type = SupportMessage.TYPE_VIDEO
            elif fname.endswith(('.mp3', '.wav', '.aac', '.m4a', '.ogg', '.flac', '.wma')):
                attachment_type = SupportMessage.TYPE_AUDIO
            else:
                attachment_type = SupportMessage.TYPE_FILE

        message = SupportMessage.objects.create(
            conversation=conversation,
            sender=request.user,
            is_from_admin=False,
            sender_name=getattr(request.user, 'name', '') or request.user.email,
            message_text=validated_data.get('message_text', '').strip(),
            attachment=attachment_file,
            attachment_type=attachment_type,
            is_read=False
        )

        # Update conversation status, timestamps, and unread admin count
        conversation.status = SupportConversation.STATUS_OPEN
        conversation.last_message_at = timezone.now()
        conversation.unread_admin_count += 1
        conversation.save(update_fields=['status', 'last_message_at', 'unread_admin_count', 'updated_at'])

        # Notify Care Team Admins via Email
        send_admin_new_message_notification(message, request=request)

        message_serializer = SupportMessageSerializer(message, context={'request': request})
        return standard_response(
            success=True,
            message="Message sent to Care Team successfully",
            data=message_serializer.data,
            status_code=status.HTTP_201_CREATED
        )


class MarkReadView(APIView):
    """
    API endpoint to mark all care team messages as read for the user
    
    POST /api/support-chat/mark-read/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication, FirebaseAuthentication]

    def post(self, request):
        conversation = get_or_create_user_support_conversation(request.user)
        unread_admin_msgs = conversation.messages.filter(is_from_admin=True, is_read=False)
        updated_count = unread_admin_msgs.count()
        if unread_admin_msgs.exists():
            now = timezone.now()
            unread_admin_msgs.update(is_read=True, read_at=now)

        conversation.unread_user_count = 0
        conversation.save(update_fields=['unread_user_count', 'updated_at'])

        return standard_response(
            success=True,
            message="All support messages marked as read",
            data={"marked_read_count": updated_count, "unread_count": 0},
            status_code=status.HTTP_200_OK
        )


# Backward-compatibility alias
MessageListView = UserConversationView