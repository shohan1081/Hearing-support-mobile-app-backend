from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import WhatNormalVideo, WhatNormalAudio


@admin.register(WhatNormalVideo)
class WhatNormalVideoAdmin(ModelAdmin):
    list_display = ('title', 'order', 'subtitle', 'duration_seconds', 'is_active', 'updated_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle', 'description')
    ordering = ('order', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'order', 'is_active')
        }),
        ('Video Description & Content', {
            'fields': ('description',)
        }),
        ('Upload Video & Thumbnail', {
            'fields': ('video_file', 'thumbnail', 'duration_seconds')
        }),
    )


@admin.register(WhatNormalAudio)
class WhatNormalAudioAdmin(ModelAdmin):
    list_display = ('title', 'order', 'subtitle', 'duration_seconds', 'is_active', 'updated_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle', 'description')
    ordering = ('order', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'order', 'is_active')
        }),
        ('Audio Description & Content', {
            'fields': ('description',)
        }),
        ('Upload Audio & Thumbnail', {
            'fields': ('audio_file', 'thumbnail', 'duration_seconds')
        }),
    )
