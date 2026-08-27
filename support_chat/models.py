from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class SupportConversation(models.Model):
    """
    Support chat conversation thread between a user and the Care Team / Admin
    """
    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_RESOLVED = 'resolved'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = (
        (STATUS_OPEN, _('Open')),
        (STATUS_IN_PROGRESS, _('In Progress')),
        (STATUS_RESOLVED, _('Resolved')),
        (STATUS_CLOSED, _('Closed')),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_conversations',
        verbose_name=_('user'),
        help_text=_("User seeking support from care team")
    )
    subject = models.CharField(
        _('subject'),
        max_length=255,
        default="Care Team Support Chat",
        help_text=_("Subject or title for this support thread")
    )
    status = models.CharField(
        _('status'),
        max_length=50,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
        help_text=_("Status of the support chat")
    )
    assigned_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_support_conversations',
        verbose_name=_('assigned admin / care specialist'),
        help_text=_("Care specialist assigned to this conversation")
    )
    last_message_at = models.DateTimeField(
        _('last message timestamp'),
        default=timezone.now,
        help_text=_("Timestamp of the most recent message in thread")
    )
    unread_user_count = models.PositiveIntegerField(
        _('unread count for user'),
        default=0,
        help_text=_("Number of unread messages waiting for the user")
    )
    unread_admin_count = models.PositiveIntegerField(
        _('unread count for admin'),
        default=0,
        help_text=_("Number of unread messages waiting for care team admin")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('support conversation')
        verbose_name_plural = _('support conversations')
        ordering = ['-last_message_at']

    def __str__(self):
        user_email = getattr(self.user, 'email', str(self.user))
        return f"Support Chat - {user_email} [{self.get_status_display()}]"

    def get_latest_message(self):
        """Return the latest message object in conversation"""
        return self.messages.order_by('-created_at').first()


class SupportMessage(models.Model):
    """
    Individual message sent within a support chat conversation.
    Supports text, pictures (images), videos, audio voice notes, and document files.
    """
    TYPE_TEXT = 'text'
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_AUDIO = 'audio'
    TYPE_FILE = 'file'

    TYPE_CHOICES = (
        (TYPE_TEXT, _('Text')),
        (TYPE_IMAGE, _('Image / Picture')),
        (TYPE_VIDEO, _('Video')),
        (TYPE_AUDIO, _('Audio / Voice Note')),
        (TYPE_FILE, _('Document / File')),
    )

    conversation = models.ForeignKey(
        SupportConversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('conversation'),
        help_text=_("Parent support conversation thread")
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_support_messages',
        verbose_name=_('sender'),
        help_text=_("User or Admin who sent this message")
    )
    is_from_admin = models.BooleanField(
        _('is from admin'),
        default=False,
        help_text=_("True if sent by care team / admin, False if sent by mobile app user")
    )
    sender_name = models.CharField(
        _('sender display name'),
        max_length=255,
        blank=True,
        help_text=_("Display name of the message sender e.g. 'Care Team', 'Dr. Sarah'")
    )
    message_text = models.TextField(
        _('message text'),
        blank=True,
        help_text=_("Text content of the message")
    )
    attachment = models.FileField(
        _('file attachment'),
        upload_to='support_chat/attachments/',
        null=True,
        blank=True,
        help_text=_("Uploaded picture, video, audio voice note, or document attachment")
    )
    attachment_type = models.CharField(
        _('attachment type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_TEXT,
        help_text=_("Type of attachment: text, image, video, audio, or file")
    )
    is_read = models.BooleanField(
        _('is read'),
        default=False,
        help_text=_("Whether the recipient has read this message")
    )
    read_at = models.DateTimeField(
        _('read timestamp'),
        null=True,
        blank=True,
        help_text=_("Timestamp when message was marked read")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('support message')
        verbose_name_plural = _('support messages')
        ordering = ['created_at']

    def __str__(self):
        sender_label = "Admin" if self.is_from_admin else "User"
        preview = self.message_text[:30] if self.message_text else f"[{self.attachment_type} attachment]"
        return f"[{sender_label}] {self.sender_name or self.sender.email}: {preview}"

    def save(self, *args, **kwargs):
        if not self.sender_name and self.sender:
            if self.is_from_admin:
                self.sender_name = getattr(self.sender, 'name', '') or "Care Team Specialist"
            else:
                self.sender_name = getattr(self.sender, 'name', '') or self.sender.email
        super().save(*args, **kwargs)

    def get_attachment_url(self, request=None):
        """Return absolute attachment file URL"""
        if self.attachment:
            try:
                url = self.attachment.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return str(self.attachment)
        return ""