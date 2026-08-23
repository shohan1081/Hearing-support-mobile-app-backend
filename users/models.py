from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import UserManager
import uuid
from django.contrib.auth.hashers import make_password, check_password


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model
    Uses email as the unique identifier instead of username
    """
    
    # Primary identifier (UUID for better security)
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the user")
    )
    
    # Required fields
    email = models.EmailField(
        _('email address'),
        unique=True,
        max_length=255,
        db_index=True,
        help_text=_("User's email address (used for login)")
    )
    
    name = models.CharField(
        _('full name'),
        max_length=150,
        help_text=_("User's full name")
    )
    
    phone_number = models.CharField(
        _('phone number'),
        max_length=20,
        null=True,
        blank=True,
        help_text=_("User's phone number")
    )
    
    date_of_birth = models.DateField(
        _('date of birth'),
        null=True,
        blank=True,
        help_text=_("User's date of birth")
    )
   
    gender = models.CharField(
        _('gender'),
        max_length=20,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
            ('prefer_not_to_say', 'Prefer not to say'),
        ],
        null=True,
        blank=True,
        help_text=_("User's gender")
    )

    occupation = models.CharField(
        _('occupation'),
        max_length=100,
        null=True,
        blank=True,
        help_text=_("User's occupation")
    )

    country = models.CharField(
        _('country'),
        max_length=100,
        null=True,
        blank=True,
        help_text=_("User's country")
    )
    
    # Status fields
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_("Designates whether this user should be treated as active.")
    )
    
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_("Designates whether the user can log into admin site.")
    )
    
    is_email_verified = models.BooleanField(
        _('email verified'),
        default=False,
        help_text=_("Designates whether user's email has been verified")
    )

    is_subscribed = models.BooleanField(
        _('subscribed'),
        default=False,
        help_text=_("Designates whether the user has an active subscription")
    )
    
    # Firebase integration
    firebase_uid = models.CharField(
        _('firebase uid'),
        max_length=128,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Firebase UID for social login integration")
    )
    
    # Authentication provider tracking
    auth_provider = models.CharField(
        _('authentication provider'),
        max_length=50,
        default='email',
        choices=[
            ('email', 'Email/Password'),
            ('google', 'Google'),
            ('apple', 'Apple'),
        ],
        help_text=_("Primary authentication method used by user")
    )
    
    # Profile picture
    profile_picture = models.ImageField(
        _('profile picture'),
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text=_("User's profile picture")
    )

    # Daily hearing machine wear time goal
    daily_wear_goal_hours = models.PositiveIntegerField(
        _('daily wear goal (hours)'),
        default=8,
        help_text=_("Target daily hearing aid wear time goal in hours (default: 8 hours, customizable by admin)")
    )

    bio = models.TextField(
        _('bio'),
        null=True,
        blank=True,
        help_text=_("User's bio")
    )
    
    # Timestamps
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
        help_text=_("Date when user registered")
    )
    
    last_login = models.DateTimeField(
        _('last login'),
        null=True,
        blank=True,
        help_text=_("Date of user's last login")
    )
    
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_("Last time user data was updated")
    )
    
    # OTP fields
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    # journal_pin = models.CharField(max_length=128, null=True, blank=True)

    # Set email as the unique identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']  # Required when creating superuser
    
    # Use custom manager
    objects = UserManager()
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['firebase_uid']),
            models.Index(fields=['is_active', 'is_email_verified']),
        ]
    
    def __str__(self):
        """String representation of user"""
        return self.email
    
    def get_full_name(self):
        """Return user's full name"""
        return self.name
    
    def get_short_name(self):
        """Return user's first name"""
        return self.name.split()[0] if self.name else self.email

    def is_otp_valid(self, expiry_minutes=10):
        """
        Check if OTP is still valid
        
        Args:
            expiry_minutes (int): Number of minutes before OTP expires
            
        Returns:
            bool: True if OTP is valid, False otherwise
        """
        if not self.otp_created_at:
            return False
        
        expiry_time = self.otp_created_at + timezone.timedelta(minutes=expiry_minutes)
        return timezone.now() < expiry_time

    def clear_otp(self):
        """Clear OTP after successful verification"""
        self.otp = None
        self.otp_created_at = None
        self.save(update_fields=['otp', 'otp_created_at'])

    @property
    def is_onboarding_completed(self):
        """Check if user has completed onboarding"""
        return hasattr(self, 'onboarding') and self.onboarding.is_completed



class AccountDeletionRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=150)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Deletion request for {self.email}"

class ProfileDataDeletionRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile data deletion request for {self.email}"

class UserLoginHistory(models.Model):
    """
    Track user login history for security purposes
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_history',
        help_text=_("User who logged in")
    )
    
    login_time = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Time of login")
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=_("IP address used for login")
    )
    
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text=_("Browser/device user agent string")
    )
    
    auth_method = models.CharField(
        max_length=50,
        default='email',
        help_text=_("Authentication method used")
    )
    
    class Meta:
        verbose_name = _('login history')
        verbose_name_plural = _('login histories')
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', '-login_time']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.login_time}"


class UserOnboarding(models.Model):
    """
    Onboarding questionnaire responses for hearing journey & goals
    """
    HEARING_JOURNEY_CHOICES = [
        ('just_received_aids', 'I just received hearing aids'),
        ('adjusting_to_aids', 'I am adjusting to hearing aids'),
        ('worn_aids_for_years', 'I have worn hearing aids for years'),
        ('need_help_with_current_aids', 'I need help with my current aids'),
        ('considering_aids', 'I am considering aids'),
    ]

    IMPROVEMENT_GOALS_CHOICES = [
        ('family_conversations', 'Hearing family conversations'),
        ('restaurants', 'Hearing in restaurants'),
        ('speech_in_noise', 'Understanding speech in noise'),
        ('tv_clearly', 'Hearing the TV clearly'),
        ('talking_on_phone', 'Talking on the phone'),
        ('church_or_meetings', 'Church or meetings'),
        ('group_conversations', 'Group conversations'),
        ('work_conversations', 'Work conversations'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='onboarding',
        help_text=_("User associated with this onboarding data")
    )
    hearing_journey = models.CharField(
        max_length=50,
        choices=HEARING_JOURNEY_CHOICES,
        help_text=_("Where user is in their hearing journey")
    )
    improvement_goals = models.JSONField(
        default=list,
        help_text=_("List of 3 hearing improvement goals selected by user")
    )
    is_completed = models.BooleanField(
        default=True,
        help_text=_("Whether onboarding has been completed")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('user onboarding')
        verbose_name_plural = _('user onboardings')

    def __str__(self):
        return f"Onboarding for {self.user.email}"


class DailyCheckIn(models.Model):
    """
    Daily Check-in for hearing status tracking ("How are you hearing today?")
    Only one check-in allowed per user per day.
    """
    HEARING_STATUS_CHOICES = [
        ('good', 'Good'),
        ('okay', 'Okay'),
        ('struggling', 'Struggling'),
        ('frustrated', 'Frustrated'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='daily_checkins',
        help_text=_("User who submitted the check-in")
    )
    hearing_status = models.CharField(
        max_length=20,
        choices=HEARING_STATUS_CHOICES,
        help_text=_("How the user is hearing today")
    )
    checkin_date = models.DateField(
        default=timezone.now,
        db_index=True,
        help_text=_("Date of the check-in")
    )
    what_went_well = models.TextField(
        null=True,
        blank=True,
        help_text=_("What went well today (for 'good' hearing status)")
    )
    what_went_okay = models.TextField(
        null=True,
        blank=True,
        help_text=_("What went okay today (for 'okay' hearing status)")
    )
    why_struggling = models.TextField(
        null=True,
        blank=True,
        help_text=_("Reason why user is struggling or frustrated (for 'struggling' / 'frustrated' hearing status)")
    )
    notes = models.TextField(
        null=True,
        blank=True,
        help_text=_("Additional notes or follow-up details")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('daily check-in')
        verbose_name_plural = _('daily check-ins')
        ordering = ['-checkin_date', '-created_at']
        unique_together = ['user', 'checkin_date']

    def __str__(self):
        return f"{self.user.email} - {self.hearing_status} on {self.checkin_date}"


class CheckInTutorial(models.Model):
    """
    Check-in Tutorial / Troubleshooting videos and instructions for users
    (e.g., "Sounds are too loud")
    """
    title = models.CharField(
        max_length=255,
        help_text=_("Tutorial title (e.g. 'Sounds are too loud')")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text=_("Unique identifier slug")
    )
    category = models.CharField(
        max_length=100,
        default="Sound Adjustment",
        help_text=_("Category/topic of the tutorial")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Detailed troubleshooting text / instructions")
    )
    video_file = models.FileField(
        upload_to='tutorials/videos/',
        null=True,
        blank=True,
        help_text=_("Upload video file directly (MP4, MOV, etc.)")
    )
    video_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text=_("External video URL (e.g. Cloudinary, S3, YouTube, Vimeo)")
    )
    thumbnail = models.ImageField(
        upload_to='tutorials/thumbnails/',
        null=True,
        blank=True,
        help_text=_("Thumbnail image for the video")
    )
    duration_seconds = models.PositiveIntegerField(
        default=0,
        blank=True,
        help_text=_("Duration of the video in seconds")
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text=_("Display order sequence")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether tutorial is active and visible in the app")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('check-in tutorial video')
        verbose_name_plural = _('check-in tutorial videos')
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def get_video_stream_url(self, request=None):
        """Return uploaded video file URL or external video_url"""
        if self.video_file:
            if request:
                return request.build_absolute_uri(self.video_file.url)
            return self.video_file.url
        return self.video_url or ""


class CheckInTutorialFeedback(models.Model):
    """
    Feedback logged when a user selects "This still feels wrong" on any tutorial
    """
    ISSUE_DURATION_CHOICES = [
        ('just_today', 'Just today'),
        ('a_few_days', 'A few days'),
        ('more_than_1_week', 'More than 1 week'),
        ('getting_worse', "It's getting worse"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tutorial_feedbacks',
        help_text=_("User who submitted feedback")
    )
    tutorial = models.ForeignKey(
        CheckInTutorial,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedbacks',
        help_text=_("Optional tutorial this feedback belongs to")
    )
    issue_duration = models.CharField(
        max_length=50,
        choices=ISSUE_DURATION_CHOICES,
        null=True,
        blank=True,
        help_text=_("How long the issue has been occurring")
    )
    other_challenge_text = models.TextField(
        null=True,
        blank=True,
        help_text=_("User response sharing what has been most challenging for 'Other' tutorial option")
    )
    notes = models.TextField(
        null=True,
        blank=True,
        help_text=_("Optional additional notes")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('check-in tutorial feedback')
        verbose_name_plural = _('check-in tutorial feedbacks')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.tutorial.title} ({self.get_issue_duration_display()})"


class HearingAidWearTime(models.Model):
    """
    Daily hearing machine / hearing aid wear time log in hours and minutes
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wear_time_logs',
        verbose_name=_('user'),
        help_text=_("User logging wear time")
    )
    date = models.DateField(
        _('date'),
        default=timezone.now,
        help_text=_("Date of wear time entry")
    )
    hours = models.PositiveIntegerField(
        _('hours'),
        default=0,
        help_text=_("Number of hours worn (0-24)")
    )
    minutes = models.PositiveIntegerField(
        _('minutes'),
        default=0,
        help_text=_("Number of minutes worn (0-59)")
    )
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_("Optional notes or environmental context")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('hearing aid wear time log')
        verbose_name_plural = _('hearing aid wear time logs')
        ordering = ['-date', '-created_at']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.email} - {self.date}: {self.hours}h {self.minutes}m"

    @property
    def total_minutes(self):
        return (self.hours * 60) + self.minutes

    @property
    def total_hours(self):
        return round(self.hours + (self.minutes / 60.0), 2)


class Appointment(models.Model):
    """
    Care team / audiologist appointment scheduled for a user.
    Can be created manually or triggered when a user reports 'struggling' or 'frustrated' in daily check-in.
    """
    STATUS_SCHEDULED = 'scheduled'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_RESCHEDULED = 'rescheduled'

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, _('Scheduled')),
        (STATUS_CONFIRMED, _('Confirmed')),
        (STATUS_COMPLETED, _('Completed')),
        (STATUS_CANCELLED, _('Cancelled')),
        (STATUS_RESCHEDULED, _('Rescheduled')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('patient / client'),
        help_text=_("Patient or client for this appointment")
    )
    checkin = models.ForeignKey(
        DailyCheckIn,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments',
        verbose_name=_('related check-in'),
        help_text=_("The daily check-in report that prompted this appointment (e.g. struggling/frustrated)")
    )
    title = models.CharField(
        _('title'),
        max_length=255,
        default="Care Team Audiologist Consultation",
        help_text=_("Appointment title or purpose (e.g. 'Hearing Aid Adjustment Consultation')")
    )
    specialist_name = models.CharField(
        _('specialist name'),
        max_length=255,
        default="Care Team Hearing Specialist",
        help_text=_("Name of the audiologist, clinician, or care specialist")
    )
    appointment_date = models.DateField(
        _('appointment date'),
        help_text=_("Date of the appointment (YYYY-MM-DD)")
    )
    appointment_time = models.TimeField(
        _('appointment time'),
        help_text=_("Time of the appointment (HH:MM)")
    )
    duration_minutes = models.PositiveIntegerField(
        _('duration (minutes)'),
        default=30,
        help_text=_("Estimated duration in minutes (e.g. 30, 45, 60)")
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SCHEDULED,
        help_text=_("Current status of the appointment")
    )
    meeting_link = models.URLField(
        _('meeting link'),
        max_length=500,
        null=True,
        blank=True,
        help_text=_("Video call or telehealth meeting link (e.g. Google Meet, Zoom)")
    )
    location = models.CharField(
        _('location'),
        max_length=255,
        default="Online Video Consultation",
        blank=True,
        help_text=_("Location or consultation channel")
    )
    notes = models.TextField(
        _('notes for client'),
        null=True,
        blank=True,
        help_text=_("Instructions or guidance visible to the client (e.g. 'Please wear your hearing aids for this call')")
    )
    admin_notes = models.TextField(
        _('internal notes'),
        null=True,
        blank=True,
        help_text=_("Internal clinician or care team notes (not shown to client)")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_appointments',
        verbose_name=_('created by admin/specialist'),
        help_text=_("Admin user who scheduled the appointment")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('care appointment')
        verbose_name_plural = _('care appointments')
        ordering = ['-appointment_date', '-appointment_time', '-created_at']

    def __str__(self):
        time_str = self.appointment_time.strftime('%I:%M %p') if self.appointment_time else ''
        return f"{self.user.email} - {self.title} on {self.appointment_date} at {time_str}"

    @property
    def is_upcoming(self):
        """Check if appointment is in the future and not cancelled/completed"""
        if self.status in [self.STATUS_CANCELLED, self.STATUS_COMPLETED]:
            return False
        import datetime
        app_dt = datetime.datetime.combine(self.appointment_date, self.appointment_time)
        if timezone.is_aware(timezone.now()):
            current_tz = timezone.get_current_timezone()
            app_dt = timezone.make_aware(app_dt, current_tz)
        return app_dt >= timezone.now()

    @property
    def formatted_date_time(self):
        """Human-readable date time string (e.g. 'Monday, Aug 25, 2026 at 10:30 AM')"""
        try:
            date_str = self.appointment_date.strftime("%A, %b %d, %Y")
            time_str = self.appointment_time.strftime("%I:%M %p").lstrip('0')
            return f"{date_str} at {time_str}"
        except Exception:
            return f"{self.appointment_date} {self.appointment_time}"


class AppointmentRequest(models.Model):
    """
    User-submitted request for a care / audiologist consultation from the mobile app.
    Admin reviews the request in the admin panel and can accept (schedule with date & time) or cancel it.
    """
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending Review')),
        (STATUS_ACCEPTED, _('Accepted & Scheduled')),
        (STATUS_CANCELLED, _('Cancelled')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointment_requests',
        verbose_name=_('user / client'),
        help_text=_("User requesting the appointment")
    )
    name = models.CharField(
        _('client name'),
        max_length=255,
        help_text=_("Full name of the client")
    )
    email = models.EmailField(
        _('email address'),
        help_text=_("Contact email address")
    )
    phone_number = models.CharField(
        _('phone number'),
        max_length=50,
        help_text=_("Contact phone number")
    )
    description = models.TextField(
        _('description / reason'),
        help_text=_("Description of hearing challenge or reason for requesting an appointment")
    )
    preferred_date = models.DateField(
        _('preferred date'),
        null=True,
        blank=True,
        help_text=_("Optional preferred date for the appointment (YYYY-MM-DD)")
    )
    preferred_time = models.CharField(
        _('preferred time'),
        max_length=100,
        null=True,
        blank=True,
        help_text=_("Optional preferred time of day (e.g. 'Morning', '2:00 PM - 4:00 PM')")
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text=_("Current review status of the appointment request")
    )
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='origin_request',
        verbose_name=_('scheduled appointment'),
        help_text=_("The scheduled appointment created by admin when accepted")
    )
    admin_notes = models.TextField(
        _('admin / care team notes'),
        null=True,
        blank=True,
        help_text=_("Internal clinician or admin notes regarding this request")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('appointment request')
        verbose_name_plural = _('appointment requests')
        ordering = ['-created_at']

    def __str__(self):
        return f"Request by {self.name} ({self.email}) - {self.get_status_display()}"


class IssueReport(models.Model):
    """
    User-submitted problem / issue report from the mobile app.
    Categories: Sound Quality, Bluetooth & Syncing, Battery & Charging, Hardware Fit & Comfort, Other.
    Admin can review issues in the admin panel and reply directly to the user via email.
    """
    CATEGORY_SOUND_QUALITY = 'sound_quality'
    CATEGORY_BLUETOOTH_SYNCING = 'bluetooth_syncing'
    CATEGORY_BATTERY_CHARGING = 'battery_charging'
    CATEGORY_HARDWARE_FIT_COMFORT = 'hardware_fit_comfort'
    CATEGORY_OTHER = 'other'

    CATEGORY_CHOICES = [
        (CATEGORY_SOUND_QUALITY, _('Sound Quality')),
        (CATEGORY_BLUETOOTH_SYNCING, _('Bluetooth & Syncing')),
        (CATEGORY_BATTERY_CHARGING, _('Battery & Charging')),
        (CATEGORY_HARDWARE_FIT_COMFORT, _('Hardware Fit & Comfort')),
        (CATEGORY_OTHER, _('Other')),
    ]

    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_RESOLVED = 'resolved'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending Review')),
        (STATUS_IN_PROGRESS, _('In Progress')),
        (STATUS_RESOLVED, _('Resolved / Replied')),
        (STATUS_CLOSED, _('Closed')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='issue_reports',
        verbose_name=_('user / client'),
        help_text=_("User reporting the issue")
    )
    user_email = models.EmailField(
        _('contact email'),
        help_text=_("Email address where admin reply will be delivered")
    )
    category = models.CharField(
        _('issue category'),
        max_length=50,
        choices=CATEGORY_CHOICES,
        help_text=_("Category: Sound Quality, Bluetooth & Syncing, Battery & Charging, Hardware Fit & Comfort, Other")
    )
    description = models.TextField(
        _('issue description'),
        help_text=_("Detailed description of the issue faced by the user")
    )
    device_model_info = models.CharField(
        _('device / OS info'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Optional device model or OS details (e.g. iPhone 15 / Hearing Aid Model X)")
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text=_("Current resolution status of this issue")
    )
    admin_reply = models.TextField(
        _('admin reply / email response'),
        blank=True,
        null=True,
        help_text=_("Care team / admin response message that will be emailed to the user")
    )
    is_reply_sent = models.BooleanField(
        _('reply email sent'),
        default=False,
        help_text=_("Whether the admin reply has been dispatched via email to the user")
    )
    replied_at = models.DateTimeField(
        _('replied at'),
        null=True,
        blank=True,
        help_text=_("Timestamp when the email reply was sent")
    )
    replied_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replied_issues',
        verbose_name=_('replied by admin'),
        help_text=_("Admin user who replied to the issue")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('issue report')
        verbose_name_plural = _('issue reports')
        ordering = ['-created_at']

    def __str__(self):
        return f"Issue #{self.id} - {self.get_category_display()} ({self.user_email}) - {self.get_status_display()}"

    def send_reply_email(self, admin_user=None):
        """Send admin reply to user via email and update reply metadata"""
        if not self.admin_reply:
            return False, "Admin reply content is empty."

        recipient_email = self.user_email or (self.user.email if self.user else None)
        if not recipient_email:
            return False, "No valid recipient email address found."

        subject = f"Care Team Support: Response to Issue #{self.id} ({self.get_category_display()})"
        user_name = self.user.get_full_name() if self.user and self.user.get_full_name() else "Valued Member"

        message = (
            f"Hello {user_name},\n\n"
            f"Thank you for reaching out to our Care Team. We have reviewed your reported issue regarding '{self.get_category_display()}'.\n\n"
            f"--------------------------------------------------\n"
            f"YOUR REPORTED ISSUE:\n"
            f"{self.description}\n"
            f"--------------------------------------------------\n\n"
            f"CARE TEAM RESPONSE:\n"
            f"{self.admin_reply}\n\n"
            f"--------------------------------------------------\n"
            f"If you need additional assistance or wish to speak directly with an audiologist, you can also request a Care Consultation directly in the Hearing App.\n\n"
            f"Warm regards,\n"
            f"Hearing Support Care Team"
        )

        from django.core.mail import send_mail
        from django.conf import settings
        from django.utils import timezone

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@hearingapp.com')

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            self.is_reply_sent = True
            self.replied_at = timezone.now()
            if admin_user and admin_user.is_authenticated:
                self.replied_by = admin_user
            if self.status == self.STATUS_PENDING:
                self.status = self.STATUS_RESOLVED
            self.save(update_fields=['is_reply_sent', 'replied_at', 'replied_by', 'status', 'updated_at'])
            return True, f"Email successfully sent to {recipient_email}"
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"