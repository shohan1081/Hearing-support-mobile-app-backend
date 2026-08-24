from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline

from .models import AIChatSession, AIChatMessage, QuickPromptSuggestion


class AIChatMessageInline(TabularInline):
    model = AIChatMessage
    extra = 0
    can_delete = False
    fields = ('sender_badge', 'message_text', 'model_name', 'tokens_used', 'created_at')
    readonly_fields = ('sender_badge', 'message_text', 'model_name', 'tokens_used', 'created_at')

    def sender_badge(self, obj):
        if obj.sender == AIChatMessage.SENDER_USER:
            return format_html('<span style="color: #2563eb; font-weight: 600;">👤 User</span>')
        elif obj.sender == AIChatMessage.SENDER_ASSISTANT:
            return format_html('<span style="color: #16a34a; font-weight: 600;">🤖 AI Assistant</span>')
        return format_html('<span style="color: #6b7280; font-weight: 600;">⚙️ System</span>')
    sender_badge.short_description = _("Sender")


@admin.register(AIChatSession)
class AIChatSessionAdmin(ModelAdmin):
    list_display = (
        'session_id_short',
        'user_name_display',
        'title',
        'message_count',
        'is_active_badge',
        'last_interaction_at',
        'created_at',
    )
    list_filter = ('is_active', 'created_at', 'last_interaction_at')
    search_fields = ('session_id', 'user__email', 'user__name', 'title')
    readonly_fields = ('session_id', 'created_at', 'updated_at', 'last_interaction_at')
    inlines = [AIChatMessageInline]

    fieldsets = (
        (_('Session Overview'), {
            'fields': ('session_id', 'user', 'title', 'is_active', 'last_interaction_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def session_id_short(self, obj):
        return str(obj.session_id)[:8] + '...'
    session_id_short.short_description = _("Session ID")

    def user_name_display(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return "-"
    user_name_display.short_description = _("User")

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = _("Messages")

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #16a34a; font-weight: 600;">● Active</span>')
        return format_html('<span style="color: #9ca3af; font-weight: 600;">○ Inactive</span>')
    is_active_badge.short_description = _("Status")


@admin.register(AIChatMessage)
class AIChatMessageAdmin(ModelAdmin):
    list_display = (
        'id',
        'session_link',
        'user_display',
        'sender_badge',
        'message_preview',
        'model_name',
        'tokens_used',
        'created_at',
    )
    list_filter = ('sender', 'model_name', 'created_at')
    search_fields = ('message_text', 'session__user__email', 'session__user__name')
    readonly_fields = ('session', 'sender', 'message_text', 'context_snapshot', 'model_name', 'tokens_used', 'created_at')

    def session_link(self, obj):
        return str(obj.session.session_id)[:8] + '...'
    session_link.short_description = _("Session")

    def user_display(self, obj):
        if obj.session and obj.session.user:
            return obj.session.user.get_full_name() or obj.session.user.email
        return "-"
    user_display.short_description = _("User")

    def sender_badge(self, obj):
        if obj.sender == AIChatMessage.SENDER_USER:
            return format_html('<span style="background-color: #dbeafe; color: #1d4ed8; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 11px;">👤 User</span>')
        elif obj.sender == AIChatMessage.SENDER_ASSISTANT:
            return format_html('<span style="background-color: #dcfce7; color: #15803d; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 11px;">🤖 AI Assistant</span>')
        return format_html('<span style="background-color: #f3f4f6; color: #374151; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 11px;">⚙️ System</span>')
    sender_badge.short_description = _("Sender")

    def message_preview(self, obj):
        return obj.message_text[:80] + '...' if len(obj.message_text) > 80 else obj.message_text
    message_preview.short_description = _("Message Text")


@admin.register(QuickPromptSuggestion)
class QuickPromptSuggestionAdmin(ModelAdmin):
    list_display = ('id', 'title', 'category_badge', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'prompt_text')

    fieldsets = (
        (_('Prompt Details'), {
            'fields': ('title', 'prompt_text', 'category', 'icon', 'order', 'is_active')
        }),
    )

    def category_badge(self, obj):
        return format_html(
            '<span style="background-color: #f1f5f9; color: #334155; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 11px;">{}</span>',
            obj.get_category_display()
        )
    category_badge.short_description = _("Category")