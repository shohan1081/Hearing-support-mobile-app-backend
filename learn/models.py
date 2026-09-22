from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from users.video_utils import (
    validate_video_file_size,
    validate_audio_file_size,
    extract_youtube_id,
    get_youtube_embed_url,
    get_youtube_thumbnail_url,
    resolve_video_data,
)


class DailyLesson(models.Model):
    """
    Admin-managed daily lesson content (video and audio) for sequential daily learning.
    Supports either direct video file upload (up to 500MB) or external Video URL / YouTube link.
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
    audio_file = models.FileField(
        _('audio file'),
        upload_to='learn/audios/',
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
        help_text=_("External audio stream URL (MP3, AAC, podcast link, etc.)")
    )
    thumbnail = models.ImageField(
        _('thumbnail'),
        upload_to='learn/thumbnails/',
        null=True,
        blank=True,
        help_text=_("Custom cover thumbnail image for the lesson (available for both file upload and YouTube/video URL)")
    )
    duration_seconds = models.PositiveIntegerField(
        _('duration in seconds'),
        default=0,
        blank=True,
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
        """Return uploaded video file URL or external video_url"""
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

    def get_audio_stream_url(self, request=None):
        """Return absolute audio file URL or audio_url"""
        if self.audio_file:
            try:
                url = self.audio_file.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return str(self.audio_file)
        return self.audio_url or ""


class WelcomeTutorial(models.Model):
    """
    Admin-managed Welcome Tutorial video for introducing users to the learning program.
    Supports either direct video file upload (up to 500MB) or external Video URL / YouTube link.
    """
    title = models.CharField(
        _('title'),
        max_length=255,
        default="Welcome to Your Hearing Journey",
        help_text=_("Welcome video title")
    )
    subtitle = models.CharField(
        _('subtitle'),
        max_length=500,
        blank=True,
        default="Get started with your daily hearing improvement plan",
        help_text=_("Short tagline or subtitle")
    )
    description = models.TextField(
        _('description'),
        blank=True,
        default="Watch this welcome video to learn how to get the most out of your daily lessons and hearing exercises.",
        help_text=_("Welcome video description and guidance notes")
    )
    video_file = models.FileField(
        _('video file'),
        upload_to='learn/welcome_videos/',
        null=True,
        blank=True,
        validators=[validate_video_file_size],
        help_text=_("Upload welcome tutorial video file directly (MP4, MOV, WebM, etc. Max: 500MB) OR enter a Video URL below.")
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
        upload_to='learn/welcome_thumbnails/',
        null=True,
        blank=True,
        help_text=_("Custom cover thumbnail image for welcome video (available for both file upload and YouTube/video URL)")
    )
    duration_seconds = models.PositiveIntegerField(
        _('duration in seconds'),
        default=0,
        blank=True,
        help_text=_("Duration of the video in seconds")
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Whether this welcome video is active and displayed to users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('welcome tutorial')
        verbose_name_plural = _('welcome tutorials')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_video_stream_url(self, request=None):
        """Return absolute video file URL or external video_url"""
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


class CheckInOverviewVideo(models.Model):
    """
    Admin-managed Check-in Overview Video explaining how daily check-ins work.
    Supports either direct video file upload (up to 500MB) or external Video URL / YouTube link.
    """
    title = models.CharField(
        _('title'),
        max_length=255,
        default="Daily Check-in Overview",
        help_text=_("Video title")
    )
    subtitle = models.CharField(
        _('subtitle'),
        max_length=500,
        blank=True,
        default="Learn how tracking your hearing daily helps your progress",
        help_text=_("Short tagline or subtitle")
    )
    description = models.TextField(
        _('description'),
        blank=True,
        default="Watch this video to understand how daily check-ins record your hearing status and personalize your journey.",
        help_text=_("Video description and guidance notes")
    )
    video_file = models.FileField(
        _('video file'),
        upload_to='learn/checkin_overview_videos/',
        null=True,
        blank=True,
        validators=[validate_video_file_size],
        help_text=_("Upload check-in overview video file directly (MP4, MOV, WebM, etc. Max: 500MB) OR enter a Video URL below.")
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
        upload_to='learn/checkin_overview_thumbnails/',
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
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Whether this video is active and displayed to users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('check-in overview video')
        verbose_name_plural = _('check-in overview videos')
        ordering = ['-created_at']

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


class CareTeamSupportVideo(models.Model):
    """
    Admin-managed Care Team Support Video explaining how audiologists & care team assist the user.
    Supports either direct video file upload (up to 500MB) or external Video URL / YouTube link.
    """
    title = models.CharField(
        _('title'),
        max_length=255,
        default="Care Team Support Guide",
        help_text=_("Video title")
    )
    subtitle = models.CharField(
        _('subtitle'),
        max_length=500,
        blank=True,
        default="Connect with your dedicated hearing care specialists",
        help_text=_("Short tagline or subtitle")
    )
    description = models.TextField(
        _('description'),
        blank=True,
        default="Watch this video to learn how our expert care team supports your hearing progress and answers your questions.",
        help_text=_("Video description and guidance notes")
    )
    video_file = models.FileField(
        _('video file'),
        upload_to='learn/care_team_videos/',
        null=True,
        blank=True,
        validators=[validate_video_file_size],
        help_text=_("Upload care team support video file directly (MP4, MOV, WebM, etc. Max: 500MB) OR enter a Video URL below.")
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
        upload_to='learn/care_team_thumbnails/',
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
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Whether this video is active and displayed to users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('care team support video')
        verbose_name_plural = _('care team support videos')
        ordering = ['-created_at']

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


class ProgressOverviewVideo(models.Model):
    """
    Admin-managed Progress Overview Video explaining how user progress and streaks are tracked.
    Supports either direct video file upload (up to 500MB) or external Video URL / YouTube link.
    """
    title = models.CharField(
        _('title'),
        max_length=255,
        default="Progress Tracking Overview",
        help_text=_("Video title")
    )
    subtitle = models.CharField(
        _('subtitle'),
        max_length=500,
        blank=True,
        default="Learn how your hearing progress and improvements are measured over time",
        help_text=_("Short tagline or subtitle")
    )
    description = models.TextField(
        _('description'),
        blank=True,
        default="Watch this video to understand how your overall progress, streaks, and milestones are tracked.",
        help_text=_("Video description and guidance notes")
    )
    video_file = models.FileField(
        _('video file'),
        upload_to='learn/progress_overview_videos/',
        null=True,
        blank=True,
        validators=[validate_video_file_size],
        help_text=_("Upload progress overview video file directly (MP4, MOV, WebM, etc. Max: 500MB) OR enter a Video URL below.")
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
        upload_to='learn/progress_overview_thumbnails/',
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
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Whether this video is active and displayed to users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('progress overview video')
        verbose_name_plural = _('progress overview videos')
        ordering = ['-created_at']

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
