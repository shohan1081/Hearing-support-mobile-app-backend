from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import DailyLesson, UserLessonProgress


@admin.register(DailyLesson)
class DailyLessonAdmin(ModelAdmin):
    list_display = ('day_number', 'title', 'subtitle', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle', 'description')
    ordering = ('day_number',)
    fieldsets = (
        (None, {
            'fields': ('day_number', 'title', 'subtitle', 'is_active')
        }),
        ('Lesson Text & Content', {
            'fields': ('description', 'key_takeaways')
        }),
        ('Upload Video & Audio', {
            'fields': (
                'video_file',
                'audio_file',
                'thumbnail',
                'duration_seconds',
            )
        }),
    )


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(ModelAdmin):
    list_display = ('user', 'get_current_day', 'start_date', 'completed_days', 'updated_at')
    search_fields = ('user__email', 'user__name')
    list_filter = ('start_date',)
    ordering = ('-updated_at',)

    def get_current_day(self, obj):
        return f"Day {obj.get_current_day()}"
    get_current_day.short_description = 'Current Day'
