from django.contrib import admin
from django import forms
from django.utils import timezone
from django.utils.html import format_html, mark_safe
from django.utils.translation import gettext_lazy as _
from django.contrib import messages as django_messages
from unfold.admin import ModelAdmin, StackedInline

from .models import SupportConversation, SupportMessage
from .utils import send_user_admin_reply_notification


class SupportConversationAdminForm(forms.ModelForm):
    """
    Custom admin form with dedicated Care Team Reply box
    """
    admin_reply_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': '💬 Type your care team reply to the client here...\n\nWhen you click SAVE below, this message will immediately be sent to the user in their mobile app support chat, and an instant email notification will be delivered to their registered email address.',
            'style': 'width: 100%; border: 2px solid #3b82f6; border-radius: 8px; padding: 12px; font-size: 14px; background: #ffffff;'
        }),
        required=False,
        label=_("💬 Care Specialist Reply Message"),
        help_text=_("Enter your response message to the client. Saving this page will deliver this message to the mobile app chat and send an email alert to the client.")
    )
    admin_reply_attachment = forms.FileField(
        required=False,
        label=_("📎 Attach File / Picture / Video / Audio (Optional)"),
        help_text=_("Upload an optional picture, video clip, audio voice note, or document to send alongside your reply.")
    )

    class Meta:
        model = SupportConversation
        fields = '__all__'


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
        elif obj.attachment_type == SupportMessage.TYPE_VIDEO:
            return format_html(
                '<video controls preload="metadata" style="max-height: 120px; max-width: 220px; border-radius: 6px;">'
                '<source src="{}">'
                'Your browser does not support video.'
                '</video>',
                url
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
    form = SupportConversationAdminForm
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
        (_('👤 Client Information'), {
            'fields': ('client_info_display',)
        }),
        (_('💬 Full Conversation History Timeline'), {
            'fields': ('conversation_chat_feed',),
            'description': _("Live chronological conversation feed between client and care specialists with picture, video, and audio player.")
        }),
        (_('✍️ Reply to Client (In-App Chat & Email Notification)'), {
            'fields': ('admin_reply_text', 'admin_reply_attachment'),
            'description': _(
                "Type your response to the user below and click SAVE (or Save and continue editing). "
                "The message will be delivered to the client's mobile app in real-time, "
                "and an email notification will be dispatched to their registered email address."
            )
        }),
        (_('⚙️ Conversation Management & Status'), {
            'fields': ('status', 'assigned_admin', 'subject', 'unread_admin_count', 'unread_user_count')
        }),
        (_('Timestamps'), {
            'fields': ('last_message_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        reply_text = form.cleaned_data.get('admin_reply_text', '').strip()
        reply_attachment = form.cleaned_data.get('admin_reply_attachment')

        if reply_text or reply_attachment:
            attachment_type = SupportMessage.TYPE_TEXT
            if reply_attachment:
                fname = reply_attachment.name.lower()
                if fname.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg')):
                    attachment_type = SupportMessage.TYPE_IMAGE
                elif fname.endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.3gp', '.m4v')):
                    attachment_type = SupportMessage.TYPE_VIDEO
                elif fname.endswith(('.mp3', '.wav', '.aac', '.m4a', '.ogg', '.flac', '.wma')):
                    attachment_type = SupportMessage.TYPE_AUDIO
                else:
                    attachment_type = SupportMessage.TYPE_FILE

            admin_name = getattr(request.user, 'name', '') or "Care Team Specialist"

            message = SupportMessage.objects.create(
                conversation=obj,
                sender=request.user,
                is_from_admin=True,
                sender_name=admin_name,
                message_text=reply_text,
                attachment=reply_attachment,
                attachment_type=attachment_type,
                is_read=False
            )

            # Mark all previous user messages as read for admin
            obj.messages.filter(is_from_admin=False, is_read=False).update(
                is_read=True,
                read_at=timezone.now()
            )

            # Update conversation state
            obj.unread_admin_count = 0
            obj.unread_user_count += 1
            obj.status = SupportConversation.STATUS_IN_PROGRESS
            obj.last_message_at = timezone.now()
            obj.assigned_admin = request.user
            obj.save(update_fields=['unread_admin_count', 'unread_user_count', 'status', 'last_message_at', 'assigned_admin', 'updated_at'])

            # Send email notification to the user
            send_user_admin_reply_notification(message, request=request)

            client_name = getattr(obj.user, 'name', '') or obj.user.email
            django_messages.success(
                request,
                format_html(
                    '✅ <strong>Care Team reply successfully sent to {}!</strong> '
                    'The message has been added to their support chat thread and an email alert was delivered.',
                    client_name
                )
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
            att_html = ""
            if msg.attachment:
                url = msg.get_attachment_url()
                if msg.attachment_type == SupportMessage.TYPE_IMAGE:
                    att_html = f'<div style="margin-top: 6px;"><a href="{url}" target="_blank"><img src="{url}" style="max-height: 120px; border-radius: 6px; border: 1px solid #e2e8f0;" /></a></div>'
                elif msg.attachment_type == SupportMessage.TYPE_VIDEO:
                    att_html = f'<div style="margin-top: 6px;"><video controls preload="metadata" style="max-height: 140px; max-width: 260px; border-radius: 6px;"><source src="{url}"></video></div>'
                elif msg.attachment_type == SupportMessage.TYPE_AUDIO:
                    att_html = f'<div style="margin-top: 6px;"><audio controls preload="none" style="height: 28px; width: 190px;"><source src="{url}"></audio></div>'
                else:
                    att_html = f'<div style="margin-top: 6px;"><a href="{url}" target="_blank" style="font-weight: 500;">📥 Download Attachment</a></div>'

            if msg.is_from_admin:
                # Care Team Message (Right Aligned, Light Green)
                sender = msg.sender_name or "Care Specialist"
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