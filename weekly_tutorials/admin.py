from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from users.direct_upload import DirectVideoUploadAdminMixin
from unfold.admin import ModelAdmin
from users.video_utils import get_video_status_badge, render_video_preview_html
from .models import WeeklyTutorial, UserWeeklyProgress


@admin.register(WeeklyTutorial)
class WeeklyTutorialAdmin(DirectVideoUploadAdminMixin, ModelAdmin):
    list_display = ('week_number', 'title', 'video_status', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('title', 'banner_text', 'description')
    ordering = ('week_number',)
    readonly_fields = ('video_preview', 'created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('week_number', 'title', 'banner_text', 'is_active')
        }),
        ('Content & Description', {
            'fields': ('description', 'what_you_will_learn')
        }),
        ('Weekly Video Media (Upload File or Enter URL)', {
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


@admin.register(UserWeeklyProgress)
class UserWeeklyProgressAdmin(ModelAdmin):
    list_display = ('user', 'get_current_week', 'journey_start_date', 'completed_weeks', 'updated_at')
    search_fields = ('user__email', 'user__name')
    list_filter = ('journey_start_date',)
    ordering = ('-updated_at',)

    def get_current_week(self, obj):
        return f"Week {obj.get_current_week()}"
    get_current_week.short_description = 'Current Week'
