from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class WeeklyTutorial(models.Model):
    """
    Admin-managed tutorial content for each week (Weeks 1 to 6)
    """
    week_number = models.PositiveIntegerField(
        _('week number'),
        unique=True,
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        help_text=_("Week number (1 to 6)")
    )
    title = models.CharField(
        _('title'),
        max_length=255,
        help_text=_("Tutorial title (e.g. 'Awareness', 'Adjustment')")
    )
    banner_text = models.TextField(
        _('banner text'),
        help_text=_("Banner / summary message shown on user dashboard (e.g. 'Your brain is waking up to more sound. This is expected.')")
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Detailed tutorial content, guide, and instructions")
    )
    video_file = models.FileField(
        _('video file'),
        upload_to='weekly_tutorials/videos/',
        null=True,
        blank=True,
        help_text=_("Upload video file directly (MP4, MOV, etc.)")
    )
    video_url = models.URLField(
        _('video url'),
        max_length=500,
        null=True,
        blank=True,
        help_text=_("External video URL (e.g. YouTube, Vimeo, Cloudinary, S3)")
    )
    thumbnail = models.ImageField(
        _('thumbnail'),
        upload_to='weekly_tutorials/thumbnails/',
        null=True,
        blank=True,
        help_text=_("Cover thumbnail image for the tutorial")
    )
    duration_seconds = models.PositiveIntegerField(
        _('duration in seconds'),
        default=0,
        blank=True,
        help_text=_("Duration of the video in seconds")
    )
    what_you_will_learn = models.JSONField(
        _('what you will learn'),
        default=list,
        blank=True,
        help_text=_("List of key takeaways/learning points (JSON list of strings)")
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Whether this tutorial is active and visible to users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('weekly tutorial')
        verbose_name_plural = _('weekly tutorials')
        ordering = ['week_number']

    def __str__(self):
        return f"Week {self.week_number}: {self.title}"

    def get_video_stream_url(self, request=None):
        """Return absolute uploaded video file URL or external video_url"""
        if self.video_file:
            if request:
                return request.build_absolute_uri(self.video_file.url)
            return self.video_file.url
        return self.video_url or ""


class UserWeeklyProgress(models.Model):
    """
    Tracks user's current week and completed weeks in their 6-week journey
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='weekly_progress',
        help_text=_("User associated with this weekly progress")
    )
    journey_start_date = models.DateField(
        _('journey start date'),
        default=timezone.now,
        help_text=_("Date when user started their 6-week hearing journey")
    )
    completed_weeks = models.JSONField(
        _('completed weeks'),
        default=list,
        blank=True,
        help_text=_("List of completed week numbers e.g. [1, 2]")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('user weekly progress')
        verbose_name_plural = _('user weekly progress records')

    def __str__(self):
        return f"{self.user.email} - Week {self.get_current_week()}"

    def get_current_week(self):
        """
        Calculate user's current week (1 to 6) based on elapsed time since journey_start_date
        """
        today = timezone.now().date()
        if today < self.journey_start_date:
            return 1
        days_diff = (today - self.journey_start_date).days
        week = (days_diff // 7) + 1
        return min(max(week, 1), 6)

    def is_week_unlocked(self, week_number):
        """Check if specific week is unlocked for user"""
        return week_number <= self.get_current_week()

    def is_week_completed(self, week_number):
        """Check if specific week is completed by user"""
        return week_number in (self.completed_weeks or [])

    def mark_week_completed(self, week_number):
        """Mark specific week as completed"""
        if not self.completed_weeks:
            self.completed_weeks = []
        if week_number not in self.completed_weeks:
            self.completed_weeks.append(week_number)
            self.save(update_fields=['completed_weeks', 'updated_at'])
