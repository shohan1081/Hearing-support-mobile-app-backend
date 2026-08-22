from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import WeeklyTutorial, UserWeeklyProgress


@admin.register(WeeklyTutorial)
class WeeklyTutorialAdmin(ModelAdmin):
    list_display = ('week_number', 'title', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('title', 'banner_text', 'description')
    ordering = ('week_number',)
    fieldsets = (
        (None, {
            'fields': ('week_number', 'title', 'banner_text', 'is_active')
        }),
        ('Content & Description', {
            'fields': ('description', 'what_you_will_learn')
        }),
        ('Media & Video', {
            'fields': ('video_file', 'video_url', 'thumbnail')
        }),
    )


@admin.register(UserWeeklyProgress)
class UserWeeklyProgressAdmin(ModelAdmin):
    list_display = ('user', 'get_current_week', 'journey_start_date', 'completed_weeks', 'updated_at')
    search_fields = ('user__email', 'user__name')
    list_filter = ('journey_start_date',)
    ordering = ('-updated_at',)

    def get_current_week(self, obj):
        return f"Week {obj.get_current_week()}"
    get_current_week.short_description = 'Current Week'
