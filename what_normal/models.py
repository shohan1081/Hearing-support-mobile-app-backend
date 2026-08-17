from django.db import models
from django.utils.translation import gettext_lazy as _


class WhatNormalVideo(models.Model):
    """
    Admin-managed video content explaining what is normal during hearing adjustment
    """
    title = models.CharField(
        _('title'),
        max_length=255,
        help_text=_("Video title (e.g. 'Understanding Loud Environmental Sounds')")
    )
    subtitle = models.CharField(
        _('subtitle'),
        max_length=500,
        blank=True,
        help_text=_("Short tagline or subtitle")
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Full description, key points, and explanatory text")
    )
    video_file = models.FileField(
        _('video file'),
        upload_to='what_normal/videos/',
        null=True,
        blank=True,
        help_text=_("Upload video file (MP4, MOV, etc.) or external link")
    )
    thumbnail = models.ImageField(
        _('thumbnail'),
        upload_to='what_normal/thumbnails/',
        null=True,
        blank=True,
        help_text=_("Cover thumbnail image")
    )
    duration_seconds = models.PositiveIntegerField(
        _('duration in seconds'),
        default=0,
        help_text=_("Duration of the video in seconds")
    )
    order = models.PositiveIntegerField(
        _('display order'),
        default=0,
        help_text=_("Ordering index (0, 1, 2...)")
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Whether this video is active and visible to users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('what\'s normal video')
        verbose_name_plural = _('what\'s normal videos')
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title

    def get_video_stream_url(self, request=None):
        """Return absolute video stream URL"""
        if self.video_file:
            try:
                url = self.video_file.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return str(self.video_file)
        return ""


class WhatNormalAudio(models.Model):
    """
    Admin-managed audio content explaining what is normal during hearing adjustment
    """
    title = models.CharField(
        _('title'),
        max_length=255,
        help_text=_("Audio track title (e.g. 'Acoustic Acclimation Audio Guide')")
    )
    subtitle = models.CharField(
        _('subtitle'),
        max_length=500,
        blank=True,
        help_text=_("Short tagline or subtitle")
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Full description, listening instructions, and notes")
    )
    audio_file = models.FileField(
        _('audio file'),
        upload_to='what_normal/audios/',
        null=True,
        blank=True,
        help_text=_("Upload audio file (MP3, WAV, AAC, etc.) or external link")
    )
    thumbnail = models.ImageField(
        _('thumbnail'),
        upload_to='what_normal/audio_thumbnails/',
        null=True,
        blank=True,
        help_text=_("Cover thumbnail image for audio track")
    )
    duration_seconds = models.PositiveIntegerField(
        _('duration in seconds'),
        default=0,
        help_text=_("Duration of the audio in seconds")
    )
    order = models.PositiveIntegerField(
        _('display order'),
        default=0,
        help_text=_("Ordering index (0, 1, 2...)")
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Whether this audio is active and visible to users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('what\'s normal audio')
        verbose_name_plural = _('what\'s normal audios')
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title

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
