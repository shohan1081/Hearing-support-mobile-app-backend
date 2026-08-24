from django.db import models
from django.utils.translation import gettext_lazy as _


class EverydayListeningTip(models.Model):
    """
    Audio strategy and tip model for Skills & Strategies.
    Categories:
    1. Everyday Listening Tips (5 audios)
    2. Communication Strategies (5 audios)
    3. Building Confidence (5 audios)
    """
    CATEGORY_EVERYDAY_LISTENING = 'everyday_listening_tips'
    CATEGORY_COMMUNICATION_STRATEGIES = 'communication_strategies'
    CATEGORY_BUILDING_CONFIDENCE = 'building_confidence'

    CATEGORY_CHOICES = (
        (CATEGORY_EVERYDAY_LISTENING, _('Everyday Listening Tips')),
        (CATEGORY_COMMUNICATION_STRATEGIES, _('Communication Strategies')),
        (CATEGORY_BUILDING_CONFIDENCE, _('Building Confidence')),
    )

    category = models.CharField(
        _('category'),
        max_length=50,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_EVERYDAY_LISTENING,
        db_index=True,
        help_text=_("Main section category")
    )
    slug = models.SlugField(
        _('slug'),
        max_length=100,
        unique=True,
        help_text=_("Unique identifier slug e.g. 'reduce-background-noise', 'start-the-conversation'")
    )
    title = models.CharField(
        _('title'),
        max_length=255,
        help_text=_("Section title e.g. 'Reduce Background Noise', 'Start the conversation'")
    )
    subtitle = models.CharField(
        _('subtitle'),
        max_length=500,
        blank=True,
        help_text=_("Short tagline or subtitle summary")
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Full explanation, practical tips, and guidance")
    )
    audio_file = models.FileField(
        _('upload audio file'),
        upload_to='skills_strategies/listening_tips/',
        null=True,
        blank=True,
        help_text=_("Upload audio file (MP3, WAV, AAC, M4A) for this strategy")
    )
    audio_url = models.URLField(
        _('audio stream URL'),
        max_length=500,
        blank=True,
        null=True,
        help_text=_("External direct audio URL or cloud stream link (used if no audio file is uploaded)")
    )
    thumbnail = models.ImageField(
        _('thumbnail image'),
        upload_to='skills_strategies/thumbnails/',
        null=True,
        blank=True,
        help_text=_("Cover thumbnail image for this strategy")
    )
    duration_seconds = models.PositiveIntegerField(
        _('duration in seconds'),
        default=0,
        blank=True,
        help_text=_("Duration of the audio in seconds (e.g. 120 = 2 minutes)")
    )
    order = models.PositiveIntegerField(
        _('display order'),
        default=0,
        help_text=_("Display order index (1, 2, 3, 4, 5)")
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Whether this strategy is active and visible to mobile users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('skills & strategy audio')
        verbose_name_plural = _('skills & strategy audios')
        ordering = ['category', 'order', 'created_at']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.order}. {self.title}"

    @property
    def duration_formatted(self):
        """Format duration into mm:ss"""
        mins = self.duration_seconds // 60
        secs = self.duration_seconds % 60
        return f"{mins}:{secs:02d}"

    def get_audio_stream_url(self, request=None):
        """Return absolute audio stream URL from file or external link"""
        if self.audio_file:
            try:
                url = self.audio_file.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return str(self.audio_file)
        if self.audio_url:
            return self.audio_url
        return ""

    def get_thumbnail_url(self, request=None):
        """Return absolute thumbnail URL"""
        if self.thumbnail:
            try:
                url = self.thumbnail.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return str(self.thumbnail)
        return ""


class EverydayListeningTipProxy(EverydayListeningTip):
    class Meta:
        proxy = True
        verbose_name = _('everyday listening tip audio')
        verbose_name_plural = _('1. Everyday Listening Tips (5 Audios)')


class CommunicationStrategyProxy(EverydayListeningTip):
    class Meta:
        proxy = True
        verbose_name = _('communication strategy audio')
        verbose_name_plural = _('2. Communication Strategies (5 Audios)')


class BuildingConfidenceTipProxy(EverydayListeningTip):
    class Meta:
        proxy = True
        verbose_name = _('building confidence audio')
        verbose_name_plural = _('3. Building Confidence (5 Audios)')