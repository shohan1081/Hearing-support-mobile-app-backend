"""
API Serializers for user authentication and profile management
All serializers follow standard response format for consistency
"""

from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .validators import (
    validate_password_strength,
    validate_email_format,
    validate_name,
    validate_date_of_birth,
    validate_password_match,
    validate_profile_picture
)
from .exceptions import (
    InvalidCredentialsException,
    EmailNotVerifiedException,
    PasswordMismatchException,
    EmailAlreadyExistsException,
)
from .utils import validate_age
from .models import HearingAidWearTime, CheckInTutorialFeedback, CheckInTutorial, DailyCheckIn, UserOnboarding

from .models import UserOnboarding, DailyCheckIn, CheckInTutorial, CheckInTutorialFeedback

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration (signup)
    
    Required fields:
    - name: User's full name
    - email: User's email address
    - password: User's password
    - confirm_password: Password confirmation
    """
    
    # Extra field for password confirmation (not in model)
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Password confirmation"
    )
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="User's password (min 8 chars, must include uppercase, lowercase, number, special char)"
    )
    
    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'name': {'required': True},
            'email': {'required': True},
        }
    
    def validate_name(self, value):
        """Validate user's name"""
        try:
            validate_name(value)
            return value
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))
    
    def validate_email(self, value):
        """Validate email format and check if it already exists"""
        # Validate email format
        try:
            validate_email_format(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))
        
        # Check if email already exists
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        
        return value.lower()
    
    def validate_password(self, value):
        """Validate password strength"""
        try:
            # Use custom validator
            validate_password_strength(value)
            
            # Also use Django's built-in validators
            django_validate_password(value)
            
            return value
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
    
    def validate(self, attrs):
        """Validate that passwords match"""
        try:
            validate_password_match(attrs['password'], attrs['confirm_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'confirm_password': str(e)})
        
        return attrs
    
    def create(self, validated_data):
        """Create new user and send OTP"""
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            is_active=False  # User is inactive until OTP verification
        )
        
        # Generate and send OTP
        from .utils import generate_otp, send_otp_email
        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save(update_fields=['otp', 'otp_created_at'])
        send_otp_email(user, otp)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    
    Required fields:
    - email: User's email address
    - password: User's password
    """
    
    email = serializers.EmailField(
        required=True,
        help_text="User's email address"
    )
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="User's password"
    )
    
    def validate(self, attrs):
        """Validate user credentials"""
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        
        if email and password:
            # Check if user exists
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise InvalidCredentialsException("Invalid email or password")
            
            # Check if user is active
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
            
            # Authenticate user
            user = authenticate(email=email, password=password)
            
            if not user:
                raise InvalidCredentialsException("Invalid email or password")
            
            # Check if email is verified (optional - uncomment if you want to enforce)
            # if not user.is_email_verified:
            #     raise EmailNotVerifiedException()
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")


class FirebaseAuthSerializer(serializers.Serializer):
    """
    Serializer for Firebase authentication (Google/Apple login)
    
    Required fields:
    - firebase_token: Firebase ID token from client
    """
    
    firebase_token = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Firebase ID token obtained from client-side Firebase authentication"
    )
    
    # Optional fields for additional user data
    email = serializers.EmailField(
        required=False,
        help_text="User's email address (optional, fallback if Apple login conceals email)"
    )

    name = serializers.CharField(
        required=False,
        help_text="User's full name (optional, will use Firebase data if not provided)"
    )
    
    date_of_birth = serializers.DateField(
        required=False,
        help_text="User's date of birth (optional)"
    )


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification
    """
    
    token = serializers.CharField(
        required=True,
        help_text="Email verification token sent to user's email"
    )


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset
    """
    
    email = serializers.EmailField(
        required=True,
        help_text="Email address of the account to reset password"
    )
    
    def validate_email(self, value):
        """Check if user with this email exists"""
        value = value.lower()
        
        if not User.objects.filter(email=value).exists():
            # For security, don't reveal if email exists or not
            # Just return the value, handle silently in view
            pass
        
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset with OTP
    """
    
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="New password"
    )
    
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Password confirmation"
    )
    
    def validate_password(self, value):
        """Validate password strength"""
        try:
            validate_password_strength(value)
            django_validate_password(value)
            return value
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
    
    def validate(self, attrs):
        """Validate that passwords match"""
        try:
            validate_password_match(attrs['password'], attrs['confirm_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'confirm_password': str(e)})
        
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing password (authenticated user)
    """
    
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Current password"
    )
    
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="New password"
    )
    
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="New password confirmation"
    )
    
    def validate_new_password(self, value):
        """Validate new password strength"""
        try:
            validate_password_strength(value)
            django_validate_password(value)
            return value
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
    
    def validate(self, attrs):
        """Validate passwords"""
        # Check if new passwords match
        try:
            validate_password_match(attrs['new_password'], attrs['confirm_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'confirm_password': str(e)})
        
        # Check if new password is different from old password
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({
                'new_password': 'New password must be different from old password.'
            })
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile (read and update)
    """
    is_onboarding_completed = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'name',
            'phone_number',
            'profile_picture',
            'auth_provider',
            'is_email_verified',
            'is_subscribed',
            'is_onboarding_completed',
            'date_joined',
            'last_login',
        ]
        read_only_fields = [
            'id',
            'email',
            'auth_provider',
            'is_email_verified',
            'is_subscribed',
            'is_onboarding_completed',
            'date_joined',
            'last_login',
        ]


class UserOnboardingSerializer(serializers.ModelSerializer):
    """
    Serializer for onboarding responses (Hearing Journey & 3 Improvement Goals)
    """
    hearing_journey_display = serializers.CharField(source='get_hearing_journey_display', read_only=True)
    improvement_goals_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserOnboarding
        fields = [
            'hearing_journey',
            'hearing_journey_display',
            'improvement_goals',
            'improvement_goals_display',
            'is_completed',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['is_completed', 'created_at', 'updated_at']

    def get_improvement_goals_display(self, obj):
        """Map goal choices to human-readable strings"""
        goals_map = dict(UserOnboarding.IMPROVEMENT_GOALS_CHOICES)
        return [goals_map.get(goal, goal) for goal in obj.improvement_goals]

    def validate_hearing_journey(self, value):
        valid_choices = [choice[0] for choice in UserOnboarding.HEARING_JOURNEY_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid hearing journey option '{value}'. Valid choices are: {', '.join(valid_choices)}"
            )
        return value

    def validate_improvement_goals(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("improvement_goals must be a list of options.")
        
        if len(value) != 3:
            raise serializers.ValidationError("You must select exactly 3 improvement goals.")
        
        valid_choices = [choice[0] for choice in UserOnboarding.IMPROVEMENT_GOALS_CHOICES]
        invalid_goals = [goal for goal in value if goal not in valid_choices]
        if invalid_goals:
            raise serializers.ValidationError(
                f"Invalid goal(s): {', '.join(invalid_goals)}. Valid choices are: {', '.join(valid_choices)}"
            )
        
        if len(set(value)) != 3:
            raise serializers.ValidationError("Duplicate improvement goals are not allowed.")
        
        return value
    
    def validate_name(self, value):
        """Validate name"""
        try:
            validate_name(value)
            return value
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))
    
    def validate_profile_picture(self, value):
        """Validate profile picture"""
        if value:
            try:
                validate_profile_picture(value)
                return value
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))
        return value


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile (only full name and profile picture)
    """
    
    class Meta:
        model = User
        fields = ['name', 'profile_picture']
    
    def validate_name(self, value):
        """Validate name"""
        try:
            validate_name(value)
            return value
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))
    
    def validate_profile_picture(self, value):
        """Validate profile picture"""
        if value:
            try:
                validate_profile_picture(value)
                return value
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))
        return value


class AccountDeleteSerializer(serializers.Serializer):
    """
    Serializer for account deletion confirmation
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Enter your password to confirm account deletion"
    )
    
    confirm_deletion = serializers.BooleanField(
        required=True,
        help_text="Must be set to true to confirm deletion"
    )
    
    def validate_confirm_deletion(self, value):
        """Ensure user confirms deletion"""
        if not value:
            raise serializers.ValidationError(
                "You must confirm that you want to delete your account."
            )
        return value


class TokenRefreshResponseSerializer(serializers.Serializer):
    """
    Serializer for token refresh response
    """
    access = serializers.CharField(help_text="New access token")
    refresh = serializers.CharField(help_text="New refresh token (if rotation enabled)")


class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer for OTP verification
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

class PasswordResetOTPVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying OTP for password reset
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

class ResendOTPSerializer(serializers.Serializer):
    """
    Serializer for resending OTP
    """
    email = serializers.EmailField()

class TokenVerifyResponseSerializer(serializers.Serializer):
    """
    Serializer for token verification response
    """
    valid = serializers.BooleanField(help_text="Whether token is valid")
    user_id = serializers.UUIDField(help_text="User ID from token", required=False)


class DailyCheckInSerializer(serializers.ModelSerializer):
    """
    Serializer for Daily Check-in ("How are you hearing today?")
    """
    hearing_status_display = serializers.CharField(source='get_hearing_status_display', read_only=True)

    class Meta:
        model = DailyCheckIn
        fields = [
            'id',
            'hearing_status',
            'hearing_status_display',
            'what_went_well',
            'what_went_okay',
            'why_struggling',
            'notes',
            'checkin_date',
            'created_at',
        ]
        read_only_fields = ['id', 'checkin_date', 'created_at']

    def validate_hearing_status(self, value):
        valid_choices = [choice[0] for choice in DailyCheckIn.HEARING_STATUS_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid hearing status '{value}'. Valid choices are: {', '.join(valid_choices)}"
            )
        return value


class CheckInTutorialSerializer(serializers.ModelSerializer):
    """
    Serializer for Check-in Tutorial / Troubleshooting videos
    """
    video_stream_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    still_feels_wrong_options = serializers.SerializerMethodField()
    other_option_flow = serializers.SerializerMethodField()

    class Meta:
        model = CheckInTutorial
        fields = [
            'id',
            'title',
            'slug',
            'category',
            'description',
            'video_stream_url',
            'video_url',
            'thumbnail_url',
            'duration_seconds',
            'order',
            'still_feels_wrong_options',
            'other_option_flow',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_video_stream_url(self, obj):
        request = self.context.get('request')
        return obj.get_video_stream_url(request=request)

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None

    def get_still_feels_wrong_options(self, obj):
        """Return 'This still feels wrong' options for mobile UI rendering"""
        options = [
            {"value": key, "label": label}
            for key, label in CheckInTutorialFeedback.ISSUE_DURATION_CHOICES
        ]
        return {
            "button_text": "This still feels wrong",
            "question": "How long has this issue been going on?",
            "type": "single_choice",
            "options": options
        }

    def get_other_option_flow(self, obj):
        """Return 'Other' challenge text flow metadata for mobile UI rendering if tutorial is 'other'"""
        if obj.slug == 'other' or obj.title.lower() == 'other':
            return {
                "has_text_input": True,
                "prompt": "What about other has been most challenging for you?",
                "field_name": "other_challenge_text",
                "input_type": "text"
            }
        return None


class CheckInTutorialFeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer for submitting 'This still feels wrong' or 'Other' option feedback on tutorials
    """
    issue_duration = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    issue_duration_display = serializers.CharField(source='get_issue_duration_display', read_only=True)
    tutorial_title = serializers.CharField(source='tutorial.title', read_only=True)

    class Meta:
        model = CheckInTutorialFeedback
        fields = [
            'id',
            'tutorial',
            'tutorial_title',
            'issue_duration',
            'issue_duration_display',
            'other_challenge_text',
            'notes',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_issue_duration(self, value):
        if not value:
            return None
        valid_choices = [choice[0] for choice in CheckInTutorialFeedback.ISSUE_DURATION_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid issue_duration '{value}'. Valid choices are: {', '.join(valid_choices)}"
            )
        return value


class HearingAidWearTimeSerializer(serializers.ModelSerializer):
    """
    Serializer for daily hearing aid wear time log
    """
    total_minutes = serializers.IntegerField(read_only=True)
    total_hours = serializers.FloatField(read_only=True)

    class Meta:
        model = HearingAidWearTime
        fields = [
            'id',
            'date',
            'hours',
            'minutes',
            'total_minutes',
            'total_hours',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HearingAidWearTimeInputSerializer(serializers.Serializer):
    """
    Input serializer for submitting or logging daily wear time in hours and minutes
    """
    date = serializers.DateField(required=False)
    hours = serializers.IntegerField(min_value=0, max_value=24, default=0)
    minutes = serializers.IntegerField(min_value=0, max_value=59, default=0)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, data):
        hrs = data.get('hours', 0)
        mins = data.get('minutes', 0)
        if hrs == 0 and mins == 0:
            raise serializers.ValidationError("Wear time duration must be greater than 0 minutes.")
        if hrs == 24 and mins > 0:
            raise serializers.ValidationError("Wear time cannot exceed 24 hours per day.")
        return data
