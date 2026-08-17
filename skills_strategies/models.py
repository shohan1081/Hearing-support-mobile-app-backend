from django.db import models
from django.utils.translation import gettext_lazy as _


class EverydayListeningTip(models.Model):
    """
    Admin-managed audio tip for Skills & Strategies - Everyday Listening Tips
    """
    slug = models.SlugField(
        _('slug'),
        max_length=100,
        unique=True,
        help_text=_("Unique identifier slug e.g. 'reduce-background-noise', 'face-the-speaker'")
    )
    title = models.CharField(
        _('title'),
        max_length=255,
        help_text=_("Tip title e.g. 'Reduce Background Noise'")
    )
    subtitle = models.CharField(
        _('subtitle'),
        max_length=500,
        blank=True,
        help_text=_("Short tagline or summary")
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Full explanation, practical steps, and listening guidance")
    )
    audio_file = models.FileField(
        _('audio file'),
        upload_to='skills_strategies/listening_tips/',
        null=True,
        blank=True,
        help_text=_("Upload audio file (MP3, WAV, AAC, etc.) or external link")
    )
    thumbnail = models.ImageField(
        _('thumbnail'),
        upload_to='skills_strategies/thumbnails/',
        null=True,
        blank=True,
        help_text=_("Cover thumbnail image for this tip")
    )
    duration_seconds = models.PositiveIntegerField(
        _('duration in seconds'),
        default=0,
        help_text=_("Duration of the audio in seconds")
    )
    order = models.PositiveIntegerField(
        _('display order'),
        default=0,
        help_text=_("Ordering index (1, 2, 3...)")
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Whether this listening tip is active and visible to users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('everyday listening tip')
        verbose_name_plural = _('everyday listening tips')
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.order}. {self.title}"

    def get_audio_stream_url(self, request=None):
        """Return absolute audio stream URL"""
        if self.audio_file:
            try:
                url = self.audio_file.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return str(self.audio_file)
        return ""
