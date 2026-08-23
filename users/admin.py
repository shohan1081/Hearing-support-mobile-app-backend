from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from datetime import time, timedelta
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.forms import UserChangeForm, UserCreationForm
from .models import (
    User,
    UserLoginHistory,
    AccountDeletionRequest,
    ProfileDataDeletionRequest,
    UserOnboarding,
    DailyCheckIn,
    CheckInTutorial,
    CheckInTutorialFeedback,
    HearingAidWearTime,
    Appointment,
    AppointmentRequest,
)
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.html import format_html


@admin.register(HearingAidWearTime)
class HearingAidWearTimeAdmin(ModelAdmin):
    list_display = ('user', 'date', 'hours', 'minutes', 'total_hours', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('user__email', 'user__name', 'notes')
    ordering = ('-date', '-created_at')


@admin.register(CheckInTutorialFeedback)
class CheckInTutorialFeedbackAdmin(ModelAdmin):
    list_display = ('user', 'tutorial', 'issue_duration', 'other_challenge_text', 'created_at')
    list_filter = ('issue_duration', 'created_at')
    search_fields = ('user__email', 'user__name', 'tutorial__title', 'other_challenge_text', 'notes')
    readonly_fields = ('created_at',)


@admin.register(CheckInTutorial)
class CheckInTutorialAdmin(ModelAdmin):
    list_display = ('title', 'category', 'video_status', 'order', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'category', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('order', 'is_active')
    readonly_fields = ('created_at', 'updated_at', 'video_preview')
    actions = ['seed_default_tutorials_action']

    def changelist_view(self, request, extra_context=None):
        """Auto-populate default check-in tutorials if database is empty"""
        if CheckInTutorial.objects.count() == 0:
            from django.core.management import call_command
            try:
                call_command('seed_checkin_tutorials')
            except Exception:
                pass
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description=_("Populate / restore default 7 check-in tutorials"))
    def seed_default_tutorials_action(self, request, queryset):
        from django.core.management import call_command
        call_command('seed_checkin_tutorials')
        self.message_user(request, "Default check-in tutorials populated and synchronized successfully.")

    fieldsets = (
        (_('Tutorial Details'), {
            'fields': (
                'title',
                'slug',
                'category',
                'description',
                ('order', 'is_active'),
            )
        }),
        (_('Video & Media Upload'), {
            'fields': (
                'video_file',
                'video_url',
                'thumbnail',
                'video_preview',
            ),
            'description': _("Upload a video file (MP4/MOV) directly or provide an external video URL. You can also upload a thumbnail image.")
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def video_status(self, obj):
        if obj.video_file:
            return format_html('<span style="color: #16a34a; font-weight: 600;">📁 Uploaded File</span>')
        elif obj.video_url:
            return format_html('<span style="color: #2563eb; font-weight: 600;">🔗 External URL</span>')
        return format_html('<span style="color: #dc2626; font-weight: 500;">❌ No Video</span>')
    video_status.short_description = _("Video Source")

    def video_preview(self, obj):
        if not obj or not obj.id:
            return _("Save tutorial first to view video preview.")
        stream_url = obj.get_video_stream_url()
        if stream_url:
            return format_html(
                '<div style="margin-top: 5px;">'
                '<video width="320" height="180" controls style="border-radius: 8px; background: #000;">'
                '<source src="{}" type="video/mp4">'
                'Your browser does not support the video tag.'
                '</video>'
                '<p style="font-size: 12px; color: #6b7280; margin-top: 4px;">'
                'Source: <a href="{}" target="_blank" style="color: #2563eb;">{}</a>'
                '</p>'
                '</div>',
                stream_url,
                stream_url,
                stream_url[:50] + '...' if len(stream_url) > 50 else stream_url
            )
        return format_html('<span style="color: #9ca3af;">No video uploaded yet.</span>')
    video_preview.short_description = _("Video Preview")


@admin.register(DailyCheckIn)
class DailyCheckInAdmin(ModelAdmin):
    """
    Daily Check-in Admin with highlighting for struggling/frustrated users
    and one-click Care Team Appointment scheduling.
    """
    list_display = (
        'user',
        'status_badge',
        'why_struggling_display',
        'checkin_date',
        'appointment_action_or_status',
        'created_at',
    )
    list_filter = ('hearing_status', 'checkin_date')
    search_fields = ('user__email', 'user__name', 'what_went_well', 'what_went_okay', 'why_struggling')
    readonly_fields = ('created_at', 'appointment_box')
    ordering = ('-checkin_date', '-created_at')

    fieldsets = (
        (None, {
            'fields': ('user', 'hearing_status', 'checkin_date')
        }),
        ('Care Consultation / Appointment', {
            'fields': ('appointment_box',),
            'description': _("Manage or schedule care appointments for clients experiencing challenges.")
        }),
        ('User Response Details', {
            'fields': ('why_struggling', 'what_went_okay', 'what_went_well', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        status_map = {
            'struggling': (
                'background-color: #fee2e2; color: #dc2626; border: 1px solid #f87171;',
                '⚠️ Struggling'
            ),
            'frustrated': (
                'background-color: #ffedd5; color: #ea580c; border: 1px solid #fb923c;',
                '🔥 Frustrated'
            ),
            'okay': (
                'background-color: #e0f2fe; color: #0284c7; border: 1px solid #bae6fd;',
                '🔵 Okay'
            ),
            'good': (
                'background-color: #dcfce7; color: #16a34a; border: 1px solid #bbf7d0;',
                '🟢 Good'
            ),
        }
        style, label = status_map.get(
            obj.hearing_status,
            ('background-color: #f3f4f6; color: #374151;', obj.hearing_status)
        )
        return format_html(
            '<span style="padding: 4px 10px; border-radius: 6px; font-weight: bold; display: inline-block; font-size: 12px; {}">{}</span>',
            style,
            label
        )
    status_badge.short_description = _("Hearing Status")

    def why_struggling_display(self, obj):
        if obj.why_struggling:
            text = obj.why_struggling.strip()
            if len(text) > 40:
                return format_html(
                    '<span title="{}">{}...</span>',
                    text,
                    text[:40]
                )
            return text
        elif obj.what_went_okay:
            return format_html('<span style="color: #6b7280;">Okay: {}</span>', obj.what_went_okay[:30])
        elif obj.what_went_well:
            return format_html('<span style="color: #16a34a;">Well: {}</span>', obj.what_went_well[:30])
        return format_html('<span style="color: #9ca3af;">—</span>')
    why_struggling_display.short_description = _("Reason / User Response")

    def appointment_action_or_status(self, obj):
        # Look for existing appointment linked to checkin or upcoming for user
        appointment = obj.appointments.first()
        if not appointment:
            appointment = Appointment.objects.filter(
                user=obj.user,
                appointment_date__gte=obj.checkin_date,
                status__in=[Appointment.STATUS_SCHEDULED, Appointment.STATUS_CONFIRMED]
            ).first()

        if appointment:
            change_url = reverse('admin:users_appointment_change', args=[appointment.id])
            time_formatted = appointment.appointment_time.strftime('%I:%M %p') if appointment.appointment_time else ''
            return format_html(
                '<a href="{}" style="background-color: #dbeafe; color: #1d4ed8; border: 1px solid #93c5fd; padding: 4px 10px; border-radius: 6px; font-weight: 600; text-decoration: none; font-size: 12px; display: inline-block;">'
                '📅 {} at {} ({})'
                '</a>',
                change_url,
                appointment.appointment_date,
                time_formatted,
                appointment.get_status_display()
            )

        if obj.hearing_status in ['struggling', 'frustrated']:
            add_url = reverse('admin:users_appointment_add') + f'?user={obj.user.id}&checkin={obj.id}&title=Care+Team+Consultation+-+{obj.hearing_status.capitalize()}'
            return format_html(
                '<a href="{}" style="background-color: #16a34a; color: white; padding: 4px 12px; border-radius: 6px; font-weight: bold; text-decoration: none; font-size: 12px; display: inline-block; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">'
                '➕ Schedule Appointment'
                '</a>',
                add_url
            )

        return format_html('<span style="color: #9ca3af;">—</span>')
    appointment_action_or_status.short_description = _("Care Team Appointment")

    def appointment_box(self, obj):
        if not obj or not obj.id:
            return _("Save check-in first to view appointment actions.")

        appointment = obj.appointments.first()
        if not appointment:
            appointment = Appointment.objects.filter(
                user=obj.user,
                appointment_date__gte=obj.checkin_date,
                status__in=[Appointment.STATUS_SCHEDULED, Appointment.STATUS_CONFIRMED]
            ).first()

        if appointment:
            change_url = reverse('admin:users_appointment_change', args=[appointment.id])
            time_formatted = appointment.appointment_time.strftime('%I:%M %p') if appointment.appointment_time else ''
            return format_html(
                '<div style="background-color: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 14px; margin: 4px 0;">'
                '<h4 style="margin: 0 0 8px 0; color: #166534; font-size: 14px; font-weight: bold;">✅ Appointment Already Scheduled</h4>'
                '<p style="margin: 0 0 8px 0; color: #374151; font-size: 13px;">'
                '<strong>Title:</strong> {}<br>'
                '<strong>Specialist:</strong> {}<br>'
                '<strong>Date & Time:</strong> {} at {}<br>'
                '<strong>Status:</strong> {}'
                '</p>'
                '<a href="{}" class="button" style="background-color: #1d4ed8; color: white; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block; font-size: 12px;">'
                '✏️ View / Edit Appointment in Admin'
                '</a>'
                '</div>',
                appointment.title,
                appointment.specialist_name,
                appointment.appointment_date,
                time_formatted,
                appointment.get_status_display(),
                change_url
            )

        if obj.hearing_status in ['struggling', 'frustrated']:
            add_url = reverse('admin:users_appointment_add') + f'?user={obj.user.id}&checkin={obj.id}&title=Care+Team+Consultation+-+{obj.hearing_status.capitalize()}'
            return format_html(
                '<div style="background-color: #fffbeb; border: 1px solid #fcd34d; border-radius: 8px; padding: 14px; margin: 4px 0;">'
                '<h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 14px; font-weight: bold;">⚠️ User Reported Struggling / Frustrated</h4>'
                '<p style="margin: 0 0 10px 0; color: #4b5563; font-size: 13px;">'
                'This patient reported difficulty with their hearing aids today. Schedule a one-on-one consultation with an audiologist to help them adjust.'
                '</p>'
                '<a href="{}" class="button" style="background-color: #16a34a; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block; font-size: 13px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
                '📅 Schedule Appointment with Date & Time for {}'
                '</a>'
                '</div>',
                add_url,
                obj.user.name or obj.user.email
            )

        return format_html(
            '<div style="color: #6b7280; font-size: 13px;">'
            'No appointment required for standard check-in. You can still '
            '<a href="{}" style="color: #2563eb; font-weight: 500;">create an appointment manually</a> if needed.'
            '</div>',
            reverse('admin:users_appointment_add') + f'?user={obj.user.id}&checkin={obj.id}'
        )
    appointment_box.short_description = _("Care Appointment Action")


@admin.register(Appointment)
class AppointmentAdmin(ModelAdmin):
    """
    Care team & audiologist appointments management in Unfold Django Admin
    """
    list_display = (
        'user',
        'title',
        'appointment_date',
        'appointment_time',
        'duration_display',
        'status_badge',
        'specialist_name',
        'meeting_link_display',
        'related_checkin_display',
        'created_at',
    )
    list_filter = ('status', 'appointment_date', 'specialist_name', 'duration_minutes')
    search_fields = ('user__email', 'user__name', 'title', 'specialist_name', 'notes', 'admin_notes', 'meeting_link')
    ordering = ('-appointment_date', '-appointment_time', '-created_at')
    readonly_fields = ('created_by', 'created_at', 'updated_at')

    fieldsets = (
        (_('Patient & Context'), {
            'fields': ('user', 'checkin', 'title')
        }),
        (_('Date, Time & Duration'), {
            'fields': (
                ('appointment_date', 'appointment_time'),
                ('duration_minutes', 'status'),
            )
        }),
        (_('Care Specialist & Meeting Details'), {
            'fields': (
                'specialist_name',
                'meeting_link',
                'location',
            )
        }),
        (_('Instructions & Notes'), {
            'fields': (
                'notes',
                'admin_notes',
            )
        }),
        (_('Audit Metadata'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        user_param = request.GET.get('user')
        checkin_param = request.GET.get('checkin')
        request_id_param = request.GET.get('request_id')
        title_param = request.GET.get('title')

        # If created from an in-app AppointmentRequest
        if request_id_param and str(request_id_param).isdigit():
            req_obj = AppointmentRequest.objects.filter(id=int(request_id_param)).first()
            if req_obj:
                initial['user'] = req_obj.user_id
                initial['title'] = f"Care Consultation - {req_obj.name}"
                if req_obj.preferred_date:
                    initial['appointment_date'] = req_obj.preferred_date
                initial['notes'] = (
                    f"Patient Request Details:\n"
                    f"• Name: {req_obj.name}\n"
                    f"• Email: {req_obj.email}\n"
                    f"• Phone: {req_obj.phone_number}\n"
                    f"• Preferred Date/Time: {req_obj.preferred_date or 'Any'} ({req_obj.preferred_time or 'Any'})\n"
                    f"• Issue: {req_obj.description}"
                )

        if user_param and not initial.get('user'):
            user_obj = User.objects.filter(id=user_param).first()
            if user_obj:
                initial['user'] = user_obj.pk
            else:
                initial['user'] = user_param

        if checkin_param:
            if str(checkin_param).isdigit():
                checkin_obj = DailyCheckIn.objects.filter(id=int(checkin_param)).first()
                if checkin_obj:
                    initial['checkin'] = checkin_obj.pk
                else:
                    initial['checkin'] = checkin_param
            else:
                initial['checkin'] = checkin_param

        if title_param:
            initial['title'] = title_param

        # Set default appointment date to tomorrow at 10:00 AM
        tomorrow = timezone.now().date() + timedelta(days=1)
        initial.setdefault('appointment_date', tomorrow)
        initial.setdefault('appointment_time', time(10, 0))
        initial.setdefault('specialist_name', 'Dr. Sarah Jenkins, Au.D.')
        initial.setdefault('meeting_link', 'https://meet.google.com/hearing-support-care')
        initial.setdefault('notes', 'Please wear your hearing aids for this consultation call so we can adjust the volume and programs together.')

        return initial

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by and request.user.is_authenticated:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

        # If this appointment was created from an AppointmentRequest, link & accept it
        request_id_param = request.GET.get('request_id')
        if request_id_param and str(request_id_param).isdigit():
            req_obj = AppointmentRequest.objects.filter(id=int(request_id_param)).first()
            if req_obj:
                req_obj.appointment = obj
                req_obj.status = AppointmentRequest.STATUS_ACCEPTED
                req_obj.save()

    def duration_display(self, obj):
        return f"{obj.duration_minutes} mins"
    duration_display.short_description = _("Duration")

    def status_badge(self, obj):
        status_styles = {
            Appointment.STATUS_SCHEDULED: ('background-color: #dbeafe; color: #1d4ed8; border: 1px solid #93c5fd;', '🗓️ Scheduled'),
            Appointment.STATUS_CONFIRMED: ('background-color: #dcfce7; color: #16a34a; border: 1px solid #86efac;', '✅ Confirmed'),
            Appointment.STATUS_COMPLETED: ('background-color: #f3f4f6; color: #374151; border: 1px solid #d1d5db;', '🏁 Completed'),
            Appointment.STATUS_CANCELLED: ('background-color: #fee2e2; color: #dc2626; border: 1px solid #fca5a5;', '❌ Cancelled'),
            Appointment.STATUS_RESCHEDULED: ('background-color: #ffedd5; color: #ea580c; border: 1px solid #fdba74;', '🔄 Rescheduled'),
        }
        style, label = status_styles.get(obj.status, ('background-color: #f3f4f6; color: #374151;', obj.status))
        return format_html(
            '<span style="padding: 3px 8px; border-radius: 6px; font-weight: bold; display: inline-block; font-size: 12px; {}">{}</span>',
            style,
            label
        )
    status_badge.short_description = _("Status")

    def meeting_link_display(self, obj):
        if obj.meeting_link:
            return format_html(
                '<a href="{}" target="_blank" style="color: #2563eb; font-weight: 500; text-decoration: underline;">🔗 Join Meeting</a>',
                obj.meeting_link
            )
        return format_html('<span style="color: #9ca3af;">—</span>')
    meeting_link_display.short_description = _("Meeting Link")

    def related_checkin_display(self, obj):
        if obj.checkin:
            change_url = reverse('admin:users_dailycheckin_change', args=[obj.checkin.id])
            status_text = obj.checkin.hearing_status.capitalize()
            return format_html(
                '<a href="{}" style="color: #4b5563; text-decoration: underline;">Check-in on {} ({})</a>',
                change_url,
                obj.checkin.checkin_date,
                status_text
            )
        return format_html('<span style="color: #9ca3af;">—</span>')
    related_checkin_display.short_description = _("Prompted By Check-in")


@admin.register(AppointmentRequest)
class AppointmentRequestAdmin(ModelAdmin):
    """
    User consultation requests submitted from the mobile app.
    Admin can review, accept (schedule appointment with date & time), or cancel.
    """
    list_display = (
        'name',
        'email',
        'phone_number',
        'status_badge',
        'description_preview',
        'preferred_date',
        'preferred_time',
        'action_or_appointment_link',
        'created_at',
    )
    list_filter = ('status', 'preferred_date', 'created_at')
    search_fields = ('name', 'email', 'phone_number', 'description', 'admin_notes', 'user__email', 'user__name')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'action_box', 'created_at', 'updated_at')
    actions = ['mark_as_cancelled_action', 'mark_as_pending_action']

    fieldsets = (
        (_('Client Contact & User'), {
            'fields': ('user', 'name', 'email', 'phone_number')
        }),
        (_('Request Details & Preference'), {
            'fields': ('description', ('preferred_date', 'preferred_time'))
        }),
        (_('Status & Care Consultation'), {
            'fields': ('status', 'appointment', 'action_box')
        }),
        (_('Internal Notes'), {
            'fields': ('admin_notes',)
        }),
        (_('Audit Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        status_styles = {
            AppointmentRequest.STATUS_PENDING: ('background-color: #fef3c7; color: #b45309; border: 1px solid #fde68a;', '🟡 Pending Review'),
            AppointmentRequest.STATUS_ACCEPTED: ('background-color: #dcfce7; color: #16a34a; border: 1px solid #86efac;', '🟢 Accepted & Scheduled'),
            AppointmentRequest.STATUS_CANCELLED: ('background-color: #fee2e2; color: #dc2626; border: 1px solid #fca5a5;', '🔴 Cancelled'),
        }
        style, label = status_styles.get(obj.status, ('background-color: #f3f4f6; color: #374151;', obj.status))
        return format_html(
            '<span style="padding: 4px 10px; border-radius: 6px; font-weight: bold; display: inline-block; font-size: 12px; {}">{}</span>',
            style,
            label
        )
    status_badge.short_description = _("Request Status")

    def description_preview(self, obj):
        if obj.description:
            text = obj.description.strip()
            if len(text) > 40:
                return format_html('<span title="{}">{}...</span>', text, text[:40])
            return text
        return format_html('<span style="color: #9ca3af;">—</span>')
    description_preview.short_description = _("Description / Reason")

    def action_or_appointment_link(self, obj):
        if obj.appointment:
            change_url = reverse('admin:users_appointment_change', args=[obj.appointment.id])
            time_formatted = obj.appointment.appointment_time.strftime('%I:%M %p') if obj.appointment.appointment_time else ''
            return format_html(
                '<a href="{}" style="background-color: #dbeafe; color: #1d4ed8; border: 1px solid #93c5fd; padding: 4px 10px; border-radius: 6px; font-weight: 600; text-decoration: none; font-size: 12px; display: inline-block;">'
                '📅 {} at {} ({})'
                '</a>',
                change_url,
                obj.appointment.appointment_date,
                time_formatted,
                obj.appointment.get_status_display()
            )

        if obj.status == AppointmentRequest.STATUS_PENDING:
            add_url = reverse('admin:users_appointment_add') + f'?user={obj.user_id}&request_id={obj.id}'
            return format_html(
                '<a href="{}" style="background-color: #16a34a; color: white; padding: 4px 12px; border-radius: 6px; font-weight: bold; text-decoration: none; font-size: 12px; display: inline-block; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">'
                '📅 Accept & Schedule'
                '</a>',
                add_url
            )

        return format_html('<span style="color: #9ca3af;">Cancelled</span>')
    action_or_appointment_link.short_description = _("Action / Consultation")

    def action_box(self, obj):
        if not obj or not obj.id:
            return _("Save request first to view actions.")

        if obj.appointment:
            change_url = reverse('admin:users_appointment_change', args=[obj.appointment.id])
            time_formatted = obj.appointment.appointment_time.strftime('%I:%M %p') if obj.appointment.appointment_time else ''
            return format_html(
                '<div style="background-color: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 14px; margin: 4px 0;">'
                '<h4 style="margin: 0 0 8px 0; color: #166534; font-size: 14px; font-weight: bold;">✅ Scheduled Appointment Linked</h4>'
                '<p style="margin: 0 0 8px 0; color: #374151; font-size: 13px;">'
                '<strong>Title:</strong> {}<br>'
                '<strong>Specialist:</strong> {}<br>'
                '<strong>Date & Time:</strong> {} at {}<br>'
                '<strong>Status:</strong> {}'
                '</p>'
                '<a href="{}" class="button" style="background-color: #1d4ed8; color: white; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block; font-size: 12px;">'
                '✏️ View / Edit Consultation in Admin'
                '</a>'
                '</div>',
                obj.appointment.title,
                obj.appointment.specialist_name,
                obj.appointment.appointment_date,
                time_formatted,
                obj.appointment.get_status_display(),
                change_url
            )

        if obj.status == AppointmentRequest.STATUS_PENDING:
            add_url = reverse('admin:users_appointment_add') + f'?user={obj.user_id}&request_id={obj.id}'
            return format_html(
                '<div style="background-color: #fffbeb; border: 1px solid #fcd34d; border-radius: 8px; padding: 14px; margin: 4px 0;">'
                '<h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 14px; font-weight: bold;">🟡 Pending Consultation Request</h4>'
                '<p style="margin: 0 0 10px 0; color: #4b5563; font-size: 13px;">'
                'Client has requested an appointment. Click below to accept the request and schedule the consultation date & time:'
                '</p>'
                '<a href="{}" class="button" style="background-color: #16a34a; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block; font-size: 13px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
                '📅 Accept & Schedule Appointment with Date/Time'
                '</a>'
                '</div>',
                add_url
            )

        return format_html(
            '<div style="color: #dc2626; font-size: 13px; background-color: #fef2f2; border: 1px solid #fecaca; padding: 10px; border-radius: 6px;">'
            'This appointment request has been marked as <strong>Cancelled</strong>.'
            '</div>'
        )
    action_box.short_description = _("Admin Care Action")

    @admin.action(description=_("Mark selected requests as Cancelled"))
    def mark_as_cancelled_action(self, request, queryset):
        count = queryset.update(status=AppointmentRequest.STATUS_CANCELLED)
        self.message_user(request, f"{count} appointment request(s) marked as Cancelled.")

    @admin.action(description=_("Mark selected requests as Pending Review"))
    def mark_as_pending_action(self, request, queryset):
        count = queryset.update(status=AppointmentRequest.STATUS_PENDING)
        self.message_user(request, f"{count} appointment request(s) marked as Pending Review.")


@admin.register(UserOnboarding)
class UserOnboardingAdmin(ModelAdmin):
    list_display = ('user', 'hearing_journey', 'is_completed', 'created_at', 'updated_at')
    list_filter = ('hearing_journey', 'is_completed', 'created_at')
    search_fields = ('user__email', 'user__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProfileDataDeletionRequest)
class ProfileDataDeletionRequestAdmin(ModelAdmin):
    list_display = ('email', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('email',)
    readonly_fields = ('email', 'user', 'created_at', 'updated_at', 'verification_token')


@admin.register(AccountDeletionRequest)
class AccountDeletionRequestAdmin(ModelAdmin):
    list_display = ('name', 'email', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'email')
    readonly_fields = ('name', 'email', 'user', 'created_at', 'updated_at', 'verification_token')


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """
    Custom User Admin with Unfold theme support
    """
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = UserChangeForm

    # Display fields in list view
    list_display = [
        'email',
        'name',
        'daily_wear_goal_hours',
        'phone_number',
        'auth_provider',
        'is_email_verified',
        'is_active',
        'is_staff',
        'date_joined',
        'last_login',
    ]
    list_editable = ['daily_wear_goal_hours']
    
    # Filters in sidebar
    list_filter = [
        'is_active',
        'is_staff',
        'is_superuser',
        'is_email_verified',
        'auth_provider',
        'date_joined',
        'last_login',
    ]
    
    # Search fields
    search_fields = ['email', 'name', 'phone_number', 'firebase_uid']
    
    # Ordering
    ordering = ['-date_joined']
    
    # Fields to display in detail view
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal Info'), {
            'fields': ('name', 'phone_number', 'date_of_birth', 'profile_picture')
        }),
        (_('Hearing Machine Goal Settings'), {
            'fields': ('daily_wear_goal_hours',)
        }),
        (_('Authentication'), {
            'fields': (
                'auth_provider',
                'firebase_uid',
                'is_email_verified',
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'date_joined', 'updated_at')
        }),
        (_('OTP'), {
            'fields': (
                'otp',
                'otp_created_at',
            ),
            'classes': ('collapse',),  # Collapsible section
        }),
    )
    
    # Fields to display when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'name',
                'date_of_birth',
                'password1',
                'password2',
                'is_active',
                'is_staff',
            ),
        }),
    )
    
    # Read-only fields
    readonly_fields = [
        'date_joined',
        'last_login',
        'updated_at',
        'otp_created_at',
    ]
    
    # Fields that can be filtered by date
    date_hierarchy = 'date_joined'
    
    # Enable bulk actions
    actions = ['activate_users', 'deactivate_users', 'verify_emails']
    
    def activate_users(self, request, queryset):
        """Bulk action to activate users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated successfully.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        """Bulk action to deactivate users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated successfully.')
    deactivate_users.short_description = 'Deactivate selected users'
    
    def verify_emails(self, request, queryset):
        """Bulk action to verify user emails"""
        updated = queryset.update(is_email_verified=True)
        self.message_user(request, f'{updated} user email(s) verified successfully.')
    verify_emails.short_description = 'Verify emails of selected users'


@admin.register(UserLoginHistory)
class UserLoginHistoryAdmin(ModelAdmin):
    """
    Admin interface for User Login History
    """
    
    # Display fields in list view
    list_display = [
        'user',
        'auth_method',
        'login_time',
        'ip_address',
        'get_user_agent_preview',
    ]
    
    # Filters in sidebar
    list_filter = [
        'auth_method',
        'login_time',
    ]
    
    # Search fields
    search_fields = [
        'user__email',
        'user__name',
        'ip_address',
    ]
    
    # Ordering
    ordering = ['-login_time']
    
    # Read-only fields (login history should not be editable)
    readonly_fields = [
        'user',
        'login_time',
        'ip_address',
        'user_agent',
        'auth_method',
    ]
    
    # Fields to display in detail view
    fields = [
        'user',
        'auth_method',
        'login_time',
        'ip_address',
        'user_agent',
    ]
    
    # Date hierarchy
    date_hierarchy = 'login_time'
    
    # Disable add and change permissions (only view)
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def get_user_agent_preview(self, obj):
        """Show preview of user agent (first 50 characters)"""
        if obj.user_agent:
            return obj.user_agent[:50] + '...' if len(obj.user_agent) > 50 else obj.user_agent
        return '-'
    get_user_agent_preview.short_description = 'User Agent'