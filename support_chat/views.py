from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from users.authentication import CustomJWTAuthentication, FirebaseAuthentication

from .models import SupportConversation, SupportMessage
from .serializers import (
    SupportMessageSerializer,
    SupportConversationListSerializer,
    SupportConversationDetailSerializer,
    SendMessageInputSerializer,
    AdminReplyInputSerializer,
)
from .utils import (
    get_or_create_user_support_conversation,
    seed_default_support_chat_sample,
    send_admin_new_message_notification,
    send_user_admin_reply_notification,
)


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


class UserConversationView(APIView):
    """
    API endpoint for mobile user to fetch their active Care Team Support Chat thread & message history
    
    GET /api/support-chat/my-conversation/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        conversation = seed_default_support_chat_sample(request.user)

        # Automatically mark admin messages in conversation as read for the user
        unread_admin_messages = conversation.messages.filter(is_from_admin=True, is_read=False)
        if unread_admin_messages.exists():
            now = timezone.now()
            unread_admin_messages.update(is_read=True, read_at=now)

        if conversation.unread_user_count > 0:
            conversation.unread_user_count = 0
            conversation.save(update_fields=['unread_user_count', 'updated_at'])

        serializer = SupportConversationDetailSerializer(conversation, context={'request': request})
        return standard_response(
            success=True,
            message="Support chat conversation retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class SendMessageView(APIView):
    """
    API endpoint for mobile user to send a message (text, image, audio voice note, file attachment) to Care Team
    
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

        # Detect attachment type automatically if file provided
        attachment_file = validated_data.get('attachment')
        attachment_type = validated_data.get('attachment_type', SupportMessage.TYPE_TEXT)
        if attachment_file and attachment_type == SupportMessage.TYPE_TEXT:
            fname = attachment_file.name.lower()
            if fname.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                attachment_type = SupportMessage.TYPE_IMAGE
            elif fname.endswith(('.mp3', '.wav', '.aac', '.m4a', '.ogg')):
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


class MessageListView(APIView):
    """
    API endpoint to list messages in the user's active support chat thread
    
    GET /api/support-chat/messages/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        conversation = get_or_create_user_support_conversation(request.user)
        messages = conversation.messages.order_by('created_at')

        # Optional filtering by since_id (for polling / incremental updates)
        since_id = request.query_params.get('since_id')
        if since_id and since_id.isdigit():
            messages = messages.filter(pk__gt=int(since_id))

        serializer = SupportMessageSerializer(messages, many=True, context={'request': request})
        return standard_response(
            success=True,
            message="Support chat messages retrieved",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class MarkReadView(APIView):
    """
    API endpoint to mark all care team messages as read for current user
    
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
            message="All care team messages marked as read",
            data={"marked_read_count": updated_count, "unread_count": 0},
            status_code=status.HTTP_200_OK
        )


class UnreadCountView(APIView):
    """
    API endpoint to get total unread care team message count for current user
    
    GET /api/support-chat/unread-count/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        conversation = get_or_create_user_support_conversation(request.user)
        unread_count = conversation.unread_user_count
        return standard_response(
            success=True,
            message="Unread count retrieved",
            data={"unread_count": unread_count},
            status_code=status.HTTP_200_OK
        )


class AdminConversationListView(APIView):
    """
    Care Team Admin API endpoint to list all user support conversations
    
    GET /api/support-chat/admin/conversations/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [CustomJWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        conversations = SupportConversation.objects.all().order_by('-last_message_at')
        status_param = request.query_params.get('status')
        if status_param:
            conversations = conversations.filter(status=status_param)

        serializer = SupportConversationListSerializer(conversations, many=True, context={'request': request})
        return standard_response(
            success=True,
            message="All support conversations retrieved for Care Team Admin",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class AdminReplyView(APIView):
    """
    Care Team Admin API endpoint to reply to a user support conversation
    
    POST /api/support-chat/admin/reply/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [CustomJWTAuthentication, FirebaseAuthentication]

    def post(self, request):
        serializer = AdminReplyInputSerializer(data=request.data)
        if not serializer.is_valid():
            return standard_response(
                success=False,
                message="Validation failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data
        conv_id = validated_data['conversation_id']
        try:
            conversation = SupportConversation.objects.get(pk=conv_id)
        except SupportConversation.DoesNotExist:
            return standard_response(
                success=False,
                message="Conversation not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        attachment_file = validated_data.get('attachment')
        attachment_type = validated_data.get('attachment_type', SupportMessage.TYPE_TEXT)

        message = SupportMessage.objects.create(
            conversation=conversation,
            sender=request.user,
            is_from_admin=True,
            sender_name=getattr(request.user, 'name', '') or "Care Team Specialist",
            message_text=validated_data.get('message_text', '').strip(),
            attachment=attachment_file,
            attachment_type=attachment_type,
            is_read=False
        )

        # Mark user's previous messages as read for admin and increment unread count for user
        conversation.messages.filter(is_from_admin=False, is_read=False).update(is_read=True, read_at=timezone.now())
        conversation.unread_admin_count = 0
        conversation.unread_user_count += 1
        conversation.status = SupportConversation.STATUS_IN_PROGRESS
        conversation.last_message_at = timezone.now()
        conversation.assigned_admin = request.user
        conversation.save(update_fields=['unread_admin_count', 'unread_user_count', 'status', 'last_message_at', 'assigned_admin', 'updated_at'])

        # Notify User via Email
        send_user_admin_reply_notification(message, request=request)

        message_serializer = SupportMessageSerializer(message, context={'request': request})
        return standard_response(
            success=True,
            message="Care Team reply sent to user successfully",
            data=message_serializer.data,
            status_code=status.HTTP_201_CREATED
        )