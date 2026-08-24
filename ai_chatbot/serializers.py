from rest_framework import serializers
from .models import AIChatSession, AIChatMessage, QuickPromptSuggestion


class AIChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for individual messages in AI chat session
    """
    sender_display = serializers.CharField(source='get_sender_display', read_only=True)

    class Meta:
        model = AIChatMessage
        fields = [
            'id',
            'sender',
            'sender_display',
            'message_text',
            'model_name',
            'tokens_used',
            'created_at',
        ]
        read_only_fields = ['id', 'sender_display', 'created_at']


class AIChatSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for listing user AI chat sessions
    """
    session_id = serializers.UUIDField(read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()

    class Meta:
        model = AIChatSession
        fields = [
            'id',
            'session_id',
            'title',
            'is_active',
            'message_count',
            'last_message_preview',
            'last_interaction_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_last_message_preview(self, obj):
        latest = obj.messages.order_by('-created_at').first()
        if latest:
            return latest.message_text[:80] + "..." if len(latest.message_text) > 80 else latest.message_text
        return ""


class AIChatSessionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed AI chat session with full history
    """
    session_id = serializers.UUIDField(read_only=True)
    messages = AIChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = AIChatSession
        fields = [
            'id',
            'session_id',
            'title',
            'is_active',
            'messages',
            'last_interaction_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class SendAIChatMessageInputSerializer(serializers.Serializer):
    """
    Input serializer for sending a question to the AI Hearing Assistant
    """
    message = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=4000,
        error_messages={
            'required': 'Question or message text is required.',
            'blank': 'Question or message cannot be blank.'
        }
    )
    session_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="Optional existing session UUID. If omitted, a new conversation session will be created automatically."
    )


class QuickPromptSuggestionSerializer(serializers.ModelSerializer):
    """
    Serializer for quick prompt suggestion chips
    """
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = QuickPromptSuggestion
        fields = [
            'id',
            'title',
            'prompt_text',
            'category',
            'category_display',
            'icon',
            'order',
        ]
        read_only_fields = fields