from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from users.video_utils import get_video_status_badge, render_video_preview_html
from .models import (
    DailyLesson,
    WelcomeTutorial,
    CheckInOverviewVideo,
    CareTeamSupportVideo,
    ProgressOverviewVideo,
    UserLessonProgress,
)


@admin.register(DailyLesson)
class DailyLessonAdmin(ModelAdmin):
    list_display = ('day_number', 'title', 'subtitle', 'video_status', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle', 'description')
    ordering = ('day_number',)
    readonly_fields = ('video_preview', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('day_number', 'title', 'subtitle', 'is_active')
        }),
        ('Lesson Text & Content', {
            'fields': ('description', 'key_takeaways')
        }),
        ('Video Media (Upload File or Enter URL)', {
            'fields': (
                'video_file',
                'video_url',
                'thumbnail',
                'video_preview',
                'duration_seconds',
            ),
            'description': _(
                "Upload a video file directly (Max 500MB) OR enter a video URL / YouTube link. "
                "For YouTube videos, ensure they are set to <strong>Unlisted</strong> so patients can play them without signing in. "
                "You can upload a custom thumbnail for either option."
            )
        }),
        ('Audio Media (Upload File or Enter Stream Link)', {
            'fields': (
                'audio_file',
                'audio_url',
            ),
            'description': _("Upload an audio file directly (Max 100MB) or enter an external audio stream URL.")
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def video_status(self, obj):
        return get_video_status_badge(obj)
    video_status.short_description = _("Video Source")

    def video_preview(self, obj):
        return render_video_preview_html(obj)
    video_preview.short_description = _("Video Preview")


@admin.register(WelcomeTutorial)
class WelcomeTutorialAdmin(ModelAdmin):
    list_display = ('title', 'subtitle', 'video_status', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle', 'description')
    readonly_fields = ('video_preview', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'is_active')
        }),
        ('Welcome Description & Guidance', {
            'fields': ('description',)
        }),
        ('Welcome Video Media (Upload File or Enter URL)', {
            'fields': (
                'video_file',
                'video_url',
                'thumbnail',
                'video_preview',
                'duration_seconds',
            ),
            'description': _(
                "Upload a video file directly (Max 500MB) OR enter a video URL / YouTube link. "
                "For YouTube videos, ensure they are set to <strong>Unlisted</strong> so patients can play them without signing in. "
                "You can upload a custom thumbnail for either option."
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def video_status(self, obj):
        return get_video_status_badge(obj)
    video_status.short_description = _("Video Source")

    def video_preview(self, obj):
        return render_video_preview_html(obj)
    video_preview.short_description = _("Video Preview")


@admin.register(CheckInOverviewVideo)
class CheckInOverviewVideoAdmin(ModelAdmin):
    list_display = ('title', 'subtitle', 'video_status', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle', 'description')
    readonly_fields = ('video_preview', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'is_active')
        }),
        ('Video Description & Guidance', {
            'fields': ('description',)
        }),
        ('Video Media (Upload File or Enter URL)', {
            'fields': (
                'video_file',
                'video_url',
                'thumbnail',
                'video_preview',
                'duration_seconds',
            ),
            'description': _(
                "Upload a video file directly (Max 500MB) OR enter a video URL / YouTube link. "
                "For YouTube videos, ensure they are set to <strong>Unlisted</strong> so patients can play them without signing in. "
                "You can upload a custom thumbnail for either option."
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def video_status(self, obj):
        return get_video_status_badge(obj)
    video_status.short_description = _("Video Source")

    def video_preview(self, obj):
        return render_video_preview_html(obj)
    video_preview.short_description = _("Video Preview")


@admin.register(CareTeamSupportVideo)
class CareTeamSupportVideoAdmin(ModelAdmin):
    list_display = ('title', 'subtitle', 'video_status', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle', 'description')
    readonly_fields = ('video_preview', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'is_active')
        }),
        ('Video Description & Guidance', {
            'fields': ('description',)
        }),
        ('Video Media (Upload File or Enter URL)', {
            'fields': (
                'video_file',
                'video_url',
                'thumbnail',
                'video_preview',
                'duration_seconds',
            ),
            'description': _(
                "Upload a video file directly (Max 500MB) OR enter a video URL / YouTube link. "
                "For YouTube videos, ensure they are set to <strong>Unlisted</strong> so patients can play them without signing in. "
                "You can upload a custom thumbnail for either option."
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def video_status(self, obj):
        return get_video_status_badge(obj)
    video_status.short_description = _("Video Source")

    def video_preview(self, obj):
        return render_video_preview_html(obj)
    video_preview.short_description = _("Video Preview")


@admin.register(ProgressOverviewVideo)
class ProgressOverviewVideoAdmin(ModelAdmin):
    list_display = ('title', 'subtitle', 'video_status', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle', 'description')
    readonly_fields = ('video_preview', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'is_active')
        }),
        ('Video Description & Guidance', {
            'fields': ('description',)
        }),
        ('Video Media (Upload File or Enter URL)', {
            'fields': (
                'video_file',
                'video_url',
                'thumbnail',
                'video_preview',
                'duration_seconds',
            ),
            'description': _(
                "Upload a video file directly (Max 500MB) OR enter a video URL / YouTube link. "
                "For YouTube videos, ensure they are set to <strong>Unlisted</strong> so patients can play them without signing in. "
                "You can upload a custom thumbnail for either option."
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def video_status(self, obj):
        return get_video_status_badge(obj)
    video_status.short_description = _("Video Source")

    def video_preview(self, obj):
        return render_video_preview_html(obj)
    video_preview.short_description = _("Video Preview")


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(ModelAdmin):
    list_display = ('user', 'get_current_day', 'start_date', 'completed_days', 'updated_at')
    search_fields = ('user__email', 'user__name')
    list_filter = ('start_date',)
    ordering = ('-updated_at',)

    def get_current_day(self, obj):
        return f"Day {obj.get_current_day()}"
    get_current_day.short_description = 'Current Day'
