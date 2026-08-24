from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .models import (
    EverydayListeningTip,
    EverydayListeningTipProxy,
    CommunicationStrategyProxy,
    BuildingConfidenceTipProxy,
)
from .utils import seed_default_everyday_listening_tips


class BaseSkillStrategyAdmin(ModelAdmin):
    list_display = (
        'order',
        'title',
        'slug',
        'audio_player_preview',
        'duration_display',
        'is_active',
        'updated_at',
    )
    list_display_links = ('title', 'slug')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'slug', 'subtitle', 'description')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order', 'created_at')
    readonly_fields = ('audio_player_preview_large', 'created_at', 'updated_at')

    fieldsets = (
        (_('Section Title & Category'), {
            'fields': ('category', 'title', 'slug', 'subtitle', 'order', 'is_active')
        }),
        (_('Strategy Guidance & Educational Content'), {
            'fields': ('description',)
        }),
        (_('Audio Upload & Player Settings'), {
            'fields': ('audio_file', 'audio_url', 'audio_player_preview_large', 'duration_seconds', 'thumbnail'),
            'description': _(
                "Upload an audio file (MP3, WAV, AAC, M4A) or provide an audio URL. "
                "The audio will be immediately playable in the mobile app."
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def changelist_view(self, request, extra_context=None):
        seed_default_everyday_listening_tips()
        return super().changelist_view(request, extra_context=extra_context)

    def audio_player_preview(self, obj):
        url = obj.get_audio_stream_url()
        if url:
            return format_html(
                '<audio controls preload="none" style="height: 30px; width: 190px;">'
                '<source src="{}" type="audio/mpeg">'
                'Your browser does not support audio.'
                '</audio>',
                url
            )
        return format_html('<span style="color: #ef4444; font-weight: 500;">⚠️ No Audio</span>')
    audio_player_preview.short_description = _("Audio Player")

    def audio_player_preview_large(self, obj):
        url = obj.get_audio_stream_url() if obj else None
        if url:
            return format_html(
                '<div style="background: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; max-width: 400px;">'
                '<p style="margin: 0 0 6px 0; font-size: 12px; font-weight: 600; color: #475569;">🎧 Current Audio Stream Preview:</p>'
                '<audio controls preload="metadata" style="width: 100%;">'
                '<source src="{}" type="audio/mpeg">'
                'Your browser does not support audio.'
                '</audio>'
                '</div>',
                url
            )
        return format_html('<span style="color: #9ca3af;">Upload an audio file or enter a URL to preview.</span>')
    audio_player_preview_large.short_description = _("Audio Preview")

    def duration_display(self, obj):
        return obj.duration_formatted
    duration_display.short_description = _("Duration")


@admin.register(EverydayListeningTipProxy)
class EverydayListeningTipAdmin(BaseSkillStrategyAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(category=EverydayListeningTip.CATEGORY_EVERYDAY_LISTENING)

    def save_model(self, request, obj, form, change):
        if not obj.category:
            obj.category = EverydayListeningTip.CATEGORY_EVERYDAY_LISTENING
        super().save_model(request, obj, form, change)


@admin.register(CommunicationStrategyProxy)
class CommunicationStrategyAdmin(BaseSkillStrategyAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(category=EverydayListeningTip.CATEGORY_COMMUNICATION_STRATEGIES)

    def save_model(self, request, obj, form, change):
        if not obj.category:
            obj.category = EverydayListeningTip.CATEGORY_COMMUNICATION_STRATEGIES
        super().save_model(request, obj, form, change)


@admin.register(BuildingConfidenceTipProxy)
class BuildingConfidenceTipAdmin(BaseSkillStrategyAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(category=EverydayListeningTip.CATEGORY_BUILDING_CONFIDENCE)

    def save_model(self, request, obj, form, change):
        if not obj.category:
            obj.category = EverydayListeningTip.CATEGORY_BUILDING_CONFIDENCE
        super().save_model(request, obj, form, change)