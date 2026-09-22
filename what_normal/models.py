from django.db import models
from django.utils.translation import gettext_lazy as _
from users.video_utils import (
    validate_video_file_size,
    validate_audio_file_size,
    extract_youtube_id,
    get_youtube_embed_url,
    get_youtube_thumbnail_url,
)


class WhatNormalVideo(models.Model):
    """
    Admin-managed video content explaining what is normal during hearing adjustment.
    Supports either direct video file upload (up to 500MB) or external Video URL / YouTube link.
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
        validators=[validate_video_file_size],
        help_text=_("Upload video file directly (MP4, MOV, WebM, etc. Max: 500MB) OR enter a Video URL below.")
    )
    video_url = models.URLField(
        _('video URL / YouTube link'),
        max_length=1000,
        null=True,
        blank=True,
        help_text=_("External video URL or YouTube link (e.g. https://www.youtube.com/watch?v=... or https://youtu.be/...). Set YouTube video to 'Unlisted' so patients can watch without signing in.")
    )
    thumbnail = models.ImageField(
        _('thumbnail'),
        upload_to='what_normal/thumbnails/',
        null=True,
        blank=True,
        help_text=_("Custom cover thumbnail image (available for both file upload and YouTube/video URL)")
    )
    duration_seconds = models.PositiveIntegerField(
        _('duration in seconds'),
        default=0,
        blank=True,
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
        """Return absolute video stream URL or external video_url"""
        if self.video_file:
            try:
                url = self.video_file.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return str(self.video_file)
        return self.video_url or ""

    def get_embed_url(self):
        """Return iframe embed URL (especially for YouTube videos)"""
        return get_youtube_embed_url(self.video_url) if self.video_url else ""

    def get_youtube_id(self):
        """Extract YouTube video ID if video_url is a YouTube link"""
        return extract_youtube_id(self.video_url) if self.video_url else None

    def is_youtube_video(self):
        """Check if video source is YouTube"""
        return bool(self.get_youtube_id())

    def get_effective_thumbnail_url(self, request=None):
        """Return custom thumbnail URL or auto YouTube thumbnail if available"""
        if self.thumbnail:
            try:
                url = self.thumbnail.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return str(self.thumbnail)
        yt_id = self.get_youtube_id()
        if yt_id:
            return get_youtube_thumbnail_url(yt_id)
        return ""


class WhatNormalAudio(models.Model):
    """
    Admin-managed audio content explaining what is normal during hearing adjustment.
    Supports either direct audio file upload (up to 100MB) or external Audio stream URL.
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
        validators=[validate_audio_file_size],
        help_text=_("Upload audio file directly (MP3, WAV, AAC, etc. Max: 100MB) OR enter an Audio URL below.")
    )
    audio_url = models.URLField(
        _('audio URL / stream link'),
        max_length=1000,
        null=True,
        blank=True,
        help_text=_("External audio stream URL (MP3, AAC, stream link, etc.)")
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
        blank=True,
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
        """Return absolute audio stream URL or audio_url"""
        if self.audio_file:
            try:
                url = self.audio_file.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return str(self.audio_file)
        return self.audio_url or ""
