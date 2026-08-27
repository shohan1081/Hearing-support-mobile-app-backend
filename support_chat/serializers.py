from rest_framework import serializers
from .models import SupportConversation, SupportMessage


class SupportMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for individual chat messages in support conversation
    """
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = SupportMessage
        fields = [
            'id',
            'conversation',
            'sender',
            'is_from_admin',
            'sender_name',
            'message_text',
            'attachment',
            'attachment_url',
            'attachment_type',
            'is_read',
            'read_at',
            'created_at',
        ]

    def get_attachment_url(self, obj):
        request = self.context.get('request')
        return obj.get_attachment_url(request=request)


class SupportConversationDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for full conversation thread with all chat messages
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = SupportConversation
        fields = [
            'id',
            'subject',
            'status',
            'status_display',
            'user_email',
            'user_name',
            'unread_user_count',
            'unread_admin_count',
            'messages',
            'last_message_at',
            'created_at',
            'updated_at',
        ]

    def get_messages(self, obj):
        msgs = obj.messages.order_by('created_at')
        return SupportMessageSerializer(msgs, many=True, context=self.context).data


class SendMessageInputSerializer(serializers.Serializer):
    """
    Input serializer for sending a chat message (text, picture/image, video, audio voice note, file attachment)
    """
    message_text = serializers.CharField(required=False, allow_blank=True)
    attachment = serializers.FileField(required=False, allow_null=True)
    attachment_type = serializers.ChoiceField(
        choices=SupportMessage.TYPE_CHOICES,
        default=SupportMessage.TYPE_TEXT,
        required=False
    )
    subject = serializers.CharField(required=False, default="Care Team Support Chat")

    def validate(self, data):
        text = data.get('message_text', '').strip()
        attachment = data.get('attachment')
        if not text and not attachment:
            raise serializers.ValidationError("Either message_text or an attachment (picture, video, audio, or document) must be provided.")
        return data


# Backward-compatibility alias
SupportConversationListSerializer = SupportConversationDetailSerializer