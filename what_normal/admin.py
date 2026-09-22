from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from users.video_utils import get_video_status_badge, render_video_preview_html
from .models import WhatNormalVideo, WhatNormalAudio


@admin.register(WhatNormalVideo)
class WhatNormalVideoAdmin(ModelAdmin):
    list_display = ('title', 'order', 'subtitle', 'video_status', 'is_active', 'updated_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle', 'description')
    ordering = ('order', 'created_at')
    readonly_fields = ('video_preview', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'order', 'is_active')
        }),
        ('Video Description & Content', {
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


@admin.register(WhatNormalAudio)
class WhatNormalAudioAdmin(ModelAdmin):
    list_display = ('title', 'order', 'subtitle', 'is_active', 'updated_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle', 'description')
    ordering = ('order', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'order', 'is_active')
        }),
        ('Audio Description & Content', {
            'fields': ('description',)
        }),
        ('Audio Media (Upload File or Enter URL)', {
            'fields': (
                'audio_file',
                'audio_url',
                'thumbnail',
                'duration_seconds',
            ),
            'description': _("Upload an audio file directly (Max 100MB) OR enter an external audio stream link.")
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
