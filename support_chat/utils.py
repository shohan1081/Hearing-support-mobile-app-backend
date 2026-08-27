from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import SupportConversation, SupportMessage

User = get_user_model()


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


def send_admin_new_message_notification(message, request=None):
    """
    Send an immediate email alert to Care Team Admins when a user sends a new support message
    """
    try:
        user = message.conversation.user
        user_name = getattr(user, 'name', '') or 'Valued User'
        user_email = getattr(user, 'email', '')
        user_phone = getattr(user, 'phone', 'N/A') or 'N/A'
        msg_text = message.message_text or f"[{message.attachment_type.upper()} Attachment]"

        admin_url = f"/admin/support_chat/supportconversation/{message.conversation.id}/change/"
        if request:
            admin_url = request.build_absolute_uri(admin_url)

        subject = f"[Care Support Alert] 💬 New Message from {user_name} ({user_email})"

        body_lines = [
            f"A new support message has arrived from a mobile app user!",
            "",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"👤 USER DETAILS",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"• Full Name: {user_name}",
            f"• Email:     {user_email}",
            f"• Phone:     {user_phone}",
            f"• Sent At:   {message.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"💬 MESSAGE CONTENT",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"\"{msg_text}\"",
            "",
        ]

        if message.attachment:
            att_url = message.get_attachment_url(request=request)
            body_lines.extend([
                f"📎 Attachment ({message.attachment_type.upper()}): {att_url}",
                ""
            ])

        body_lines.extend([
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"👉 VIEW & REPLY IN ADMIN PANEL:",
            f"{admin_url}",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ])

        plain_body = "\n".join(body_lines)

        # Collect recipient admin emails
        admin_emails = list(
            User.objects.filter(is_staff=True, is_active=True)
            .exclude(email='')
            .values_list('email', flat=True)
        )
        if not admin_emails:
            default_from = getattr(settings, 'DEFAULT_FROM_EMAIL', '')
            if default_from:
                admin_emails = [default_from]

        if admin_emails:
            send_mail(
                subject=subject,
                message=plain_body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hearingapp.com'),
                recipient_list=admin_emails,
                fail_silently=True
            )
            return True
    except Exception as e:
        print(f"Failed to send admin support chat notification: {e}")
    return False


def send_user_admin_reply_notification(message, request=None):
    """
    Send an email notification to the user when Care Team Admin replies
    """
    try:
        user = message.conversation.user
        if not user or not user.email:
            return False

        user_name = getattr(user, 'name', '') or 'User'
        sender_name = message.sender_name or "Care Team Specialist"
        msg_text = message.message_text or f"[{message.attachment_type.upper()} Attachment]"

        subject = f"Hearing Care Support: New Reply from {sender_name}"

        plain_body = (
            f"Hello {user_name},\n\n"
            f"You have received a new reply from your Hearing Care Specialist:\n\n"
            f"\"{msg_text}\"\n\n"
            f"Please open the Hearing Support Mobile App to view the full response and continue the conversation.\n\n"
            f"Warm regards,\n"
            f"Hearing Care Support Team"
        )

        send_mail(
            subject=subject,
            message=plain_body,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hearingapp.com'),
            recipient_list=[user.email],
            fail_silently=True
        )
        return True
    except Exception as e:
        print(f"Failed to send user support chat reply notification: {e}")
    return False