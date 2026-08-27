from django.contrib import admin
from django import forms
from django.utils import timezone
from django.utils.html import format_html, mark_safe
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from django.contrib import messages as django_messages
from unfold.admin import ModelAdmin, StackedInline

from .models import SupportConversation, SupportMessage
from .utils import send_user_admin_reply_notification


class SupportMessageInline(StackedInline):
    model = SupportMessage
    extra = 0
    readonly_fields = ('sender', 'is_from_admin', 'sender_name', 'media_preview', 'created_at')
    fields = ('sender', 'is_from_admin', 'sender_name', 'message_text', 'attachment', 'attachment_type', 'media_preview', 'is_read', 'created_at')
    ordering = ('created_at',)

    def media_preview(self, obj):
        if not obj or not obj.attachment:
            return "-"
        url = obj.get_attachment_url()
        if obj.attachment_type == SupportMessage.TYPE_IMAGE:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height: 120px; border-radius: 6px; border: 1px solid #e2e8f0;" />'
                '</a>',
                url, url
            )
        elif obj.attachment_type == SupportMessage.TYPE_AUDIO:
            return format_html(
                '<audio controls preload="none" style="height: 30px; width: 220px;">'
                '<source src="{}" type="audio/mpeg">'
                'Your browser does not support audio.'
                '</audio>',
                url
            )
        return format_html('<a href="{}" target="_blank" style="color: #2563eb; font-weight: 500;">📥 Download File Attachment</a>', url)
    media_preview.short_description = _("Media Preview")


@admin.register(SupportConversation)
class SupportConversationAdmin(ModelAdmin):
    list_display = (
        'id',
        'client_name_badge',
        'user_email',
        'status_badge',
        'unread_admin_badge',
        'message_count_badge',
        'last_message_preview',
        'last_message_at',
    )
    list_display_links = ('id', 'client_name_badge', 'user_email')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'user__name', 'user__phone', 'subject')
    readonly_fields = (
        'client_info_display',
        'conversation_chat_feed',
        'unread_user_count',
        'unread_admin_count',
        'last_message_at',
        'created_at',
        'updated_at',
    )
    ordering = ('-last_message_at',)
    inlines = [SupportMessageInline]

    fieldsets = (
        (_('Client Information'), {
            'fields': ('client_info_display',)
        }),
        (_('Conversation Thread & Full Chat History'), {
            'fields': ('conversation_chat_feed',),
            'description': _("Live chronological conversation feed between client and care team specialists.")
        }),
        (_('Conversation Management & Care Status'), {
            'fields': ('subject', 'status', 'assigned_admin', 'unread_admin_count', 'unread_user_count')
        }),
        (_('Timestamps'), {
            'fields': ('last_message_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def client_name_badge(self, obj):
        name = getattr(obj.user, 'name', '') or 'User'
        return format_html(
            '<div style="font-weight: 600; color: #1e293b;">👤 {}</div>',
            name
        )
    client_name_badge.short_description = _('Client Name')

    def user_email(self, obj):
        return obj.user.email if obj.user else "-"
    user_email.short_description = _('User Email')

    def status_badge(self, obj):
        colors = {
            SupportConversation.STATUS_OPEN: ('#fef3c7', '#d97706', '🟡 Open'),
            SupportConversation.STATUS_IN_PROGRESS: ('#e0f2fe', '#0284c7', '🔵 In Progress'),
            SupportConversation.STATUS_RESOLVED: ('#dcfce7', '#16a34a', '🟢 Resolved'),
            SupportConversation.STATUS_CLOSED: ('#f1f5f9', '#64748b', '⚪ Closed'),
        }
        bg, text, label = colors.get(obj.status, ('#f1f5f9', '#64748b', obj.status))
        return format_html(
            '<span style="background: {}; color: {}; padding: 3px 8px; border-radius: 9999px; font-weight: 600; font-size: 11px;">{}</span>',
            bg, text, label
        )
    status_badge.short_description = _('Status')

    def unread_admin_badge(self, obj):
        if obj.unread_admin_count > 0:
            return format_html(
                '<span style="background: #fee2e2; color: #dc2626; padding: 4px 8px; border-radius: 6px; font-weight: 700; font-size: 12px; border: 1px solid #fca5a5;">🔴 {} New Message(s)</span>',
                obj.unread_admin_count
            )
        return format_html('<span style="color: #10b981; font-weight: 500;">✓ Read</span>')
    unread_admin_badge.short_description = _('Care Team Attention')

    def message_count_badge(self, obj):
        count = obj.messages.count()
        return format_html('<span style="font-weight: 600; color: #475569;">💬 {} msgs</span>', count)
    message_count_badge.short_description = _('Total Msgs')

    def last_message_preview(self, obj):
        latest = obj.get_latest_message()
        if latest:
            sender = "Care Specialist" if latest.is_from_admin else "Client"
            msg = latest.message_text[:35] if latest.message_text else f"[{latest.attachment_type} attachment]"
            return f"[{sender}] {msg}"
        return "No messages yet"
    last_message_preview.short_description = _('Latest Message')

    def client_info_display(self, obj):
        if not obj or not obj.user:
            return "-"
        u = obj.user
        name = getattr(u, 'name', '') or 'N/A'
        email = getattr(u, 'email', '') or 'N/A'
        phone = getattr(u, 'phone', '') or 'N/A'
        dob = getattr(u, 'date_of_birth', None)
        dob_str = dob.strftime('%b %d, %Y') if dob else 'Not specified'
        goal = getattr(u, 'daily_goal_hours', 8)
        joined = u.date_joined.strftime('%b %d, %Y') if getattr(u, 'date_joined', None) else 'N/A'

        return format_html(
            '<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 8px;">'
            '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">'
            '<div><span style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase;">Client Name</span><br><strong style="font-size: 14px; color: #0f172a;">{}</strong></div>'
            '<div><span style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase;">Email Address</span><br><strong style="font-size: 14px; color: #0f172a;">{}</strong></div>'
            '<div><span style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase;">Phone Number</span><br><strong style="font-size: 14px; color: #0f172a;">{}</strong></div>'
            '<div><span style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase;">Date of Birth</span><br><strong style="font-size: 14px; color: #0f172a;">{}</strong></div>'
            '<div><span style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase;">Daily Wear Goal</span><br><strong style="font-size: 14px; color: #0f172a;">{} hours/day</strong></div>'
            '<div><span style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase;">Member Since</span><br><strong style="font-size: 14px; color: #0f172a;">{}</strong></div>'
            '</div>'
            '</div>',
            name, email, phone, dob_str, goal, joined
        )
    client_info_display.short_description = _("Client Overview Card")

    def conversation_chat_feed(self, obj):
        if not obj:
            return "-"
        messages = obj.messages.order_by('created_at')
        if not messages.exists():
            return format_html('<p style="color: #94a3b8; font-style: italic;">No messages in this conversation yet.</p>')

        html_blocks = ['<div style="background: #f1f5f9; padding: 16px; border-radius: 8px; max-height: 480px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; border: 1px solid #cbd5e1;">']
        for msg in messages:
            created = msg.created_at.strftime('%b %d, %Y %I:%M %p')
            if msg.is_from_admin:
                # Care Team Message (Right Aligned, Light Green)
                sender = msg.sender_name or "Care Specialist"
                att_html = ""
                if msg.attachment:
                    url = msg.get_attachment_url()
                    if msg.attachment_type == SupportMessage.TYPE_IMAGE:
                        att_html = f'<div style="margin-top: 6px;"><a href="{url}" target="_blank"><img src="{url}" style="max-height: 100px; border-radius: 6px;" /></a></div>'
                    elif msg.attachment_type == SupportMessage.TYPE_AUDIO:
                        att_html = f'<div style="margin-top: 6px;"><audio controls preload="none" style="height: 28px; width: 180px;"><source src="{url}"></audio></div>'
                    else:
                        att_html = f'<div style="margin-top: 6px;"><a href="{url}" target="_blank" style="color: #047857; font-weight: 500;">📥 Attachment</a></div>'

                html_blocks.append(
                    f'<div style="align-self: flex-end; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 12px 12px 2px 12px; padding: 10px 14px; max-width: 75%;">'
                    f'<div style="font-size: 11px; font-weight: 700; color: #047857;">🩺 {sender} <span style="font-weight: 400; color: #6ee7b7; margin-left: 6px;">{created}</span></div>'
                    f'<div style="font-size: 13px; color: #065f46; margin-top: 4px; white-space: pre-wrap;">{msg.message_text or ""}</div>'
                    f'{att_html}'
                    f'</div>'
                )
            else:
                # User Message (Left Aligned, Light Blue)
                sender = msg.sender_name or getattr(obj.user, 'name', '') or obj.user.email
                att_html = ""
                if msg.attachment:
                    url = msg.get_attachment_url()
                    if msg.attachment_type == SupportMessage.TYPE_IMAGE:
                        att_html = f'<div style="margin-top: 6px;"><a href="{url}" target="_blank"><img src="{url}" style="max-height: 100px; border-radius: 6px;" /></a></div>'
                    elif msg.attachment_type == SupportMessage.TYPE_AUDIO:
                        att_html = f'<div style="margin-top: 6px;"><audio controls preload="none" style="height: 28px; width: 180px;"><source src="{url}"></audio></div>'
                    else:
                        att_html = f'<div style="margin-top: 6px;"><a href="{url}" target="_blank" style="color: #1d4ed8; font-weight: 500;">📥 Attachment</a></div>'

                html_blocks.append(
                    f'<div style="align-self: flex-start; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px 12px 12px 2px; padding: 10px 14px; max-width: 75%;">'
                    f'<div style="font-size: 11px; font-weight: 700; color: #1d4ed8;">👤 {sender} <span style="font-weight: 400; color: #93c5fd; margin-left: 6px;">{created}</span></div>'
                    f'<div style="font-size: 13px; color: #1e3a8a; margin-top: 4px; white-space: pre-wrap;">{msg.message_text or ""}</div>'
                    f'{att_html}'
                    f'</div>'
                )

        html_blocks.append('</div>')
        return mark_safe(''.join(html_blocks))
    conversation_chat_feed.short_description = _("Live Message Timeline")


@admin.register(SupportMessage)
class SupportMessageAdmin(ModelAdmin):
    list_display = (
        'id',
        'sender_type_badge',
        'user_badge',
        'message_preview',
        'attachment_preview',
        'read_badge',
        'created_at',
    )
    list_display_links = ('id', 'sender_type_badge', 'user_badge')
    list_filter = ('is_from_admin', 'is_read', 'attachment_type', 'created_at')
    search_fields = (
        'message_text',
        'sender__email',
        'sender__name',
        'sender_name',
        'conversation__user__email',
        'conversation__user__name'
    )
    ordering = ('-created_at',)
    readonly_fields = ('media_viewer', 'created_at')

    fieldsets = (
        (_('Sender & Conversation Context'), {
            'fields': ('conversation', 'sender', 'is_from_admin', 'sender_name')
        }),
        (_('Message Content & Media Attachment'), {
            'fields': ('message_text', 'attachment', 'attachment_type', 'media_viewer')
        }),
        (_('Read Receipt & Audit'), {
            'fields': ('is_read', 'read_at', 'created_at')
        }),
    )

    def sender_type_badge(self, obj):
        if obj.is_from_admin:
            return format_html('<span style="background: #dcfce7; color: #16a34a; padding: 3px 8px; border-radius: 9999px; font-weight: 600; font-size: 11px;">🩺 Care Team</span>')
        return format_html('<span style="background: #eff6ff; color: #2563eb; padding: 3px 8px; border-radius: 9999px; font-weight: 600; font-size: 11px;">👤 User</span>')
    sender_type_badge.short_description = _('Sender Type')

    def user_badge(self, obj):
        user = obj.conversation.user if obj.conversation and obj.conversation.user else obj.sender
        name = getattr(user, 'name', '') or ''
        email = getattr(user, 'email', '')
        display = f"{name} ({email})" if name else email
        return format_html('<div style="font-weight: 500; color: #1e293b;">{}</div>', display)
    user_badge.short_description = _('User / Client')

    def message_preview(self, obj):
        if obj.message_text:
            return obj.message_text[:50]
        if obj.attachment:
            return f"[{obj.attachment_type.upper()} Attachment]"
        return "-"
    message_preview.short_description = _('Message Text')

    def attachment_preview(self, obj):
        if not obj.attachment:
            return format_html('<span style="color: #94a3b8;">None</span>')
        url = obj.get_attachment_url()
        if obj.attachment_type == SupportMessage.TYPE_IMAGE:
            return format_html('<a href="{}" target="_blank">🖼️ Image</a>', url)
        elif obj.attachment_type == SupportMessage.TYPE_AUDIO:
            return format_html(
                '<audio controls preload="none" style="height: 26px; width: 150px;"><source src="{}"></audio>',
                url
            )
        return format_html('<a href="{}" target="_blank">📎 File</a>', url)
    attachment_preview.short_description = _('Attachment')

    def read_badge(self, obj):
        if not obj.is_read:
            return format_html('<span style="background: #fee2e2; color: #dc2626; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 11px;">🔴 NEW</span>')
        return format_html('<span style="color: #10b981; font-weight: 500;">✓ Read</span>')
    read_badge.short_description = _('Read Status')

    def media_viewer(self, obj):
        if not obj or not obj.attachment:
            return format_html('<span style="color: #9ca3af;">No file attached.</span>')
        url = obj.get_attachment_url()
        if obj.attachment_type == SupportMessage.TYPE_IMAGE:
            return format_html(
                '<div style="margin-top: 6px;">'
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height: 200px; border-radius: 8px; border: 1px solid #e2e8f0;" />'
                '</a>'
                '</div>',
                url, url
            )
        elif obj.attachment_type == SupportMessage.TYPE_AUDIO:
            return format_html(
                '<div style="margin-top: 6px;">'
                '<audio controls preload="metadata" style="width: 320px;">'
                '<source src="{}" type="audio/mpeg">'
                'Your browser does not support audio.'
                '</audio>'
                '</div>',
                url
            )
        return format_html(
            '<div style="margin-top: 6px;">'
            '<a href="{}" target="_blank" style="display: inline-block; background: #f1f5f9; padding: 8px 14px; border-radius: 6px; border: 1px solid #cbd5e1; font-weight: 600; color: #1e293b;">📥 Download File ({})</a>'
            '</div>',
            url, obj.attachment.name
        )
    media_viewer.short_description = _("Media Viewer")