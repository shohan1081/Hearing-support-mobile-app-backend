from django.contrib import admin
from django import forms
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages as django_messages
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from .models import SupportConversation, SupportMessage


class SupportMessageInline(StackedInline):
    model = SupportMessage
    extra = 0
    readonly_fields = ('sender', 'is_from_admin', 'sender_name', 'created_at')
    fields = ('sender', 'is_from_admin', 'sender_name', 'message_text', 'attachment', 'attachment_type', 'is_read', 'created_at')
    ordering = ('created_at',)


class QuickReplyForm(forms.Form):
    reply_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type reply message to send to user...'}),
        label="Quick Reply to User",
        required=True
    )


@admin.register(SupportConversation)
class SupportConversationAdmin(ModelAdmin):
    list_display = ('user_email', 'subject', 'status', 'unread_admin_badge', 'last_message_preview', 'last_message_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'user__name', 'subject')
    readonly_fields = ('unread_user_count', 'unread_admin_count', 'last_message_at', 'created_at', 'updated_at')
    ordering = ('-last_message_at',)
    inlines = [SupportMessageInline]

    fieldsets = (
        (None, {
            'fields': ('user', 'subject', 'status', 'assigned_admin')
        }),
        ('Unread Counters & Timestamps', {
            'fields': ('unread_user_count', 'unread_admin_count', 'last_message_at', 'created_at', 'updated_at')
        }),
    )

    def user_email(self, obj):
        return obj.user.email if obj.user else "-"
    user_email.short_description = 'User Email'

    def unread_admin_badge(self, obj):
        if obj.unread_admin_count > 0:
            return f"🔴 {obj.unread_admin_count} New Message(s)"
        return "🟢 Read"
    unread_admin_badge.short_description = 'Care Team Unread'

    def last_message_preview(self, obj):
        latest = obj.get_latest_message()
        if latest:
            sender = "Admin" if latest.is_from_admin else "User"
            msg = latest.message_text[:40] if latest.message_text else f"[{latest.attachment_type} attachment]"
            return f"[{sender}] {msg}"
        return "No messages yet"
    last_message_preview.short_description = 'Last Message'


@admin.register(SupportMessage)
class SupportMessageAdmin(ModelAdmin):
    list_display = ('id', 'conversation_user', 'sender_display', 'is_from_admin', 'message_preview', 'attachment_type', 'is_read', 'created_at')
    list_filter = ('is_from_admin', 'attachment_type', 'is_read', 'created_at')
    search_fields = ('message_text', 'sender__email', 'sender_name', 'conversation__user__email')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('conversation', 'sender', 'is_from_admin', 'sender_name')
        }),
        ('Message Content & Media Attachment', {
            'fields': ('message_text', 'attachment', 'attachment_type')
        }),
        ('Read Status', {
            'fields': ('is_read', 'read_at')
        }),
    )

    def conversation_user(self, obj):
        return obj.conversation.user.email if obj.conversation and obj.conversation.user else "-"
    conversation_user.short_description = 'User'

    def sender_display(self, obj):
        return obj.sender_name or (obj.sender.email if obj.sender else "-")
    sender_display.short_description = 'Sender'

    def message_preview(self, obj):
        if obj.message_text:
            return obj.message_text[:45]
        if obj.attachment:
            return f"[{obj.attachment_type.upper()} Attachment]"
        return "-"
    message_preview.short_description = 'Content'
