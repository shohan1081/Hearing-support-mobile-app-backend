import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class AIChatSession(models.Model):
    """
    AI Hearing Assistant chat conversation session for a user
    """
    session_id = models.UUIDField(
        _('session id'),
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_chat_sessions',
        verbose_name=_('user')
    )
    title = models.CharField(
        _('session title'),
        max_length=255,
        default="Hearing Improvement Assistant",
        help_text=_("Auto-generated or user-defined title for this chat topic")
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Active chat session flag")
    )
    last_interaction_at = models.DateTimeField(
        _('last interaction at'),
        default=timezone.now
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('AI chat session')
        verbose_name_plural = _('AI chat sessions')
        ordering = ['-last_interaction_at']

    def __str__(self):
        user_email = getattr(self.user, 'email', str(self.user))
        return f"AI Chat - {user_email} - {self.title} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    def get_recent_history(self, limit=12):
        """Return the most recent messages for OpenAI context window"""
        return self.messages.exclude(sender='system').order_by('-created_at')[:limit][::-1]


class AIChatMessage(models.Model):
    """
    Individual message turn within an AI chat session
    """
    SENDER_USER = 'user'
    SENDER_ASSISTANT = 'assistant'
    SENDER_SYSTEM = 'system'

    SENDER_CHOICES = (
        (SENDER_USER, _('User')),
        (SENDER_ASSISTANT, _('AI Assistant')),
        (SENDER_SYSTEM, _('System Context')),
    )

    session = models.ForeignKey(
        AIChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('session')
    )
    sender = models.CharField(
        _('sender'),
        max_length=20,
        choices=SENDER_CHOICES,
        default=SENDER_USER
    )
    message_text = models.TextField(
        _('message text'),
        help_text=_("Text content of the message")
    )
    context_snapshot = models.JSONField(
        _('user context snapshot'),
        default=dict,
        blank=True,
        null=True,
        help_text=_("Snapshot of user hearing score, wear time, and app state when message was sent")
    )
    model_name = models.CharField(
        _('AI model'),
        max_length=50,
        blank=True,
        default='gpt-4o-mini',
        help_text=_("OpenAI model used to generate assistant response")
    )
    tokens_used = models.PositiveIntegerField(
        _('tokens used'),
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('AI chat message')
        verbose_name_plural = _('AI chat messages')
        ordering = ['created_at']

    def __str__(self):
        snippet = self.message_text[:40] + '...' if len(self.message_text) > 40 else self.message_text
        return f"[{self.get_sender_display()}] {snippet}"


class QuickPromptSuggestion(models.Model):
    """
    Suggested quick prompts displayed in the mobile chatbot home UI
    """
    CATEGORY_HEARING_SCORE = 'hearing_score'
    CATEGORY_NOISY_ENVIRONMENTS = 'noisy_environments'
    CATEGORY_TINNITUS = 'tinnitus'
    CATEGORY_PROGRESS = 'progress'
    CATEGORY_DEVICE_CARE = 'device_care'
    CATEGORY_GENERAL = 'general'

    CATEGORY_CHOICES = (
        (CATEGORY_HEARING_SCORE, _('Hearing Score')),
        (CATEGORY_NOISY_ENVIRONMENTS, _('Noisy Environments')),
        (CATEGORY_TINNITUS, _('Tinnitus Support')),
        (CATEGORY_PROGRESS, _('Progress Tracking')),
        (CATEGORY_DEVICE_CARE, _('Device Care & Bluetooth')),
        (CATEGORY_GENERAL, _('General')),
    )

    title = models.CharField(
        _('prompt title'),
        max_length=150,
        help_text=_("Short label e.g. 'Improve Hearing Score'")
    )
    prompt_text = models.TextField(
        _('prompt question text'),
        help_text=_("Full query sent to AI e.g. 'How can I improve my hearing score?'")
    )
    category = models.CharField(
        _('category'),
        max_length=50,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_GENERAL
    )
    icon = models.CharField(
        _('material icon name'),
        max_length=50,
        default='help_outline',
        blank=True,
        help_text=_("Material icon name for UI display e.g. 'trending_up', 'volume_up', 'hearing'")
    )
    order = models.PositiveIntegerField(
        _('display order'),
        default=0
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('quick prompt suggestion')
        verbose_name_plural = _('quick prompt suggestions')
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"