from django.utils import timezone
from .models import SupportConversation, SupportMessage


def get_or_create_user_support_conversation(user, subject="Care Team Support Chat"):
    """
    Get active open support conversation for user or create one
    """
    conversation = SupportConversation.objects.filter(
        user=user,
        status__in=[SupportConversation.STATUS_OPEN, SupportConversation.STATUS_IN_PROGRESS]
    ).first()

    if not conversation:
        conversation = SupportConversation.objects.create(
            user=user,
            subject=subject,
            status=SupportConversation.STATUS_OPEN,
            last_message_at=timezone.now()
        )
    return conversation


def seed_default_support_chat_sample(user):
    """
    Populate a sample welcome message from Care Team if conversation is new
    """
    conversation = get_or_create_user_support_conversation(user)
    if not conversation.messages.exists():
        SupportMessage.objects.create(
            conversation=conversation,
            sender=user,
            is_from_admin=True,
            sender_name="Care Team Specialist",
            message_text="Hello! Welcome to the Hearing Care Support Team. How can we assist you with your hearing plan or device today?",
            attachment_type=SupportMessage.TYPE_TEXT,
            is_read=True
        )
        conversation.last_message_at = timezone.now()
        conversation.save(update_fields=['last_message_at', 'updated_at'])
    return conversation
