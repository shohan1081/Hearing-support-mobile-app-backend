from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class DailyLesson(models.Model):
    """
    Admin-managed daily lesson content (video and audio) for sequential daily learning
    """
    day_number = models.PositiveIntegerField(
        _('day number'),
        unique=True,
        validators=[MinValueValidator(1)],
        help_text=_("Sequential day number (1, 2, 3...)")
    )
    title = models.CharField(
        _('title'),
        max_length=255,
        help_text=_("Lesson title (e.g. 'Day 1: Introduction to Sound Perception')")
    )
    subtitle = models.CharField(
        _('subtitle'),
        max_length=500,
        blank=True,
        help_text=_("Short summary or subtitle for today's lesson")
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Detailed lesson text, instructions, and notes")
    )
    video_file = models.FileField(
        _('video file'),
        upload_to='learn/videos/',
        null=True,
        blank=True,
        help_text=_("Upload video file (MP4, MOV, etc.) or external link")
    )
    audio_file = models.FileField(
        _('audio file'),
        upload_to='learn/audios/',
        null=True,
        blank=True,
        help_text=_("Upload audio file (MP3, WAV, AAC, etc.) or external link")
    )
    thumbnail = models.ImageField(
        _('thumbnail'),
        upload_to='learn/thumbnails/',
        null=True,
        blank=True,
        help_text=_("Cover thumbnail image for the lesson")
    )
    duration_seconds = models.PositiveIntegerField(
        _('duration in seconds'),
        default=0,
        help_text=_("Duration of the media in seconds")
    )
    key_takeaways = models.JSONField(
        _('key takeaways'),
        default=list,
        blank=True,
        help_text=_("List of key learning points (JSON list of strings)")
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Whether this lesson is active and visible to users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('daily lesson')
        verbose_name_plural = _('daily lessons')
        ordering = ['day_number']

    def __str__(self):
        return f"Day {self.day_number}: {self.title}"

    def get_video_stream_url(self, request=None):
        """Return absolute video file URL"""
        if self.video_file:
            try:
                url = self.video_file.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return str(self.video_file)
        return ""

    def get_audio_stream_url(self, request=None):
        """Return absolute audio file URL"""
        if self.audio_file:
            try:
                url = self.audio_file.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return str(self.audio_file)
        return ""


class UserLessonProgress(models.Model):
    """
    Tracks user's current day and completed days in their daily sequential learning journey
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        help_text=_("User associated with this lesson progress")
    )
    start_date = models.DateField(
        _('learning start date'),
        default=timezone.now,
        help_text=_("Date when user started their daily learning journey")
    )
    completed_days = models.JSONField(
        _('completed days'),
        default=list,
        blank=True,
        help_text=_("List of completed day numbers e.g. [1, 2, 3]")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('user lesson progress')
        verbose_name_plural = _('user lesson progress records')

    def __str__(self):
        return f"{self.user.email} - Day {self.get_current_day()}"

    def get_current_day(self):
        """
        Calculate user's current day number (1, 2, 3...) based on days elapsed since start_date
        """
        today = timezone.now().date()
        if today < self.start_date:
            return 1
        days_elapsed = (today - self.start_date).days + 1
        return max(days_elapsed, 1)

    def is_day_unlocked(self, day_number):
        """Check if specific day is unlocked for user"""
        return day_number <= self.get_current_day()

    def is_day_completed(self, day_number):
        """Check if specific day is marked completed by user"""
        return day_number in (self.completed_days or [])

    def mark_day_completed(self, day_number):
        """Mark specific day as completed"""
        if not self.completed_days:
            self.completed_days = []
        if day_number not in self.completed_days:
            self.completed_days.append(day_number)
            self.save(update_fields=['completed_days', 'updated_at'])
