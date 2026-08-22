from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    FirebaseAuthView,
    VerifyOTPView,
    ResendOTPView,
    PasswordResetRequestView,
    PasswordResetOTPVerifyView,
    PasswordResetConfirmView,  # Add this import
    PasswordChangeView,
    UserProfileView,
    AccountDeleteView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    OnboardingView,
    OnboardingOptionsView,
    DailyCheckInView,
    DailyCheckInOptionsView,
    CheckInTutorialListView,
    CheckInTutorialDetailView,
    CheckInTutorialFeedbackView,
    account_deletion_request_view,
    AccountDeletionAPIView,
    VerifyAccountDeletionView,
    delete_profile_data_request_view,
    ProfileDataDeletionAPIView,
    VerifyProfileDataDeletionView,
    HearingAidWearTimeView,
    HearingScoreView,
    TodayWearTimeView,
    DailyActivityScoreView,
    ProgressChartView,
    UserWearGoalView,
    ConsistencyReportView,
    UserAppointmentListView,
    UpcomingAppointmentView,
    UserAppointmentDetailView,
    AppointmentRequestCreateView,
    UserAppointmentRequestListView,
    UserAppointmentRequestDetailView,
)

app_name = 'users'

urlpatterns = [
    # Wear Time, Activity Score & Progress Chart APIs
    path('wear-time/', HearingAidWearTimeView.as_view(), name='wear-time'),
    path('today-wear-time/', TodayWearTimeView.as_view(), name='today-wear-time'),
    path('hearing-score/', HearingScoreView.as_view(), name='hearing-score'),
    path('daily-activity-score/', DailyActivityScoreView.as_view(), name='daily-activity-score'),
    path('progress-chart/', ProgressChartView.as_view(), name='progress-chart'),
    path('consistency-report/', ConsistencyReportView.as_view(), name='consistency-report'),
    path('wear-goal/', UserWearGoalView.as_view(), name='wear-goal'),

    # Authentication endpoints
    path('signup/', UserRegistrationView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('firebase-auth/', FirebaseAuthView.as_view(), name='firebase-auth'),
    
    # Token management
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', CustomTokenVerifyView.as_view(), name='token-verify'),
    
    # OTP verification
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    
    # Password management
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-otp-verify/', PasswordResetOTPVerifyView.as_view(), name='password-reset-otp-verify'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('password-change/', PasswordChangeView.as_view(), name='password-change'),
    
    # Profile, Onboarding & Daily Check-in management
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('account-delete/', AccountDeleteView.as_view(), name='account-delete'),
    path('onboarding/', OnboardingView.as_view(), name='onboarding'),
    path('onboarding/options/', OnboardingOptionsView.as_view(), name='onboarding-options'),
    path('checkin/', DailyCheckInView.as_view(), name='daily-checkin'),
    path('checkin/options/', DailyCheckInOptionsView.as_view(), name='daily-checkin-options'),

    # Care Appointments & Consultation Requests
    path('appointments/', UserAppointmentListView.as_view(), name='user-appointments-list'),
    path('appointments/upcoming/', UpcomingAppointmentView.as_view(), name='user-upcoming-appointment'),
    path('appointments/<int:pk>/', UserAppointmentDetailView.as_view(), name='user-appointment-detail'),
    path('appointments/request/', AppointmentRequestCreateView.as_view(), name='appointment-request-create'),
    path('appointments/requests/', UserAppointmentRequestListView.as_view(), name='user-appointment-requests-list'),
    path('appointments/requests/<int:pk>/', UserAppointmentRequestDetailView.as_view(), name='user-appointment-request-detail'),

    # Check-in Tutorials
    path('checkin-tutorials/', CheckInTutorialListView.as_view(), name='checkin-tutorial-list'),
    path('checkin-tutorials/feedback/', CheckInTutorialFeedbackView.as_view(), name='checkin-tutorial-feedback'),
    path('checkin-tutorials/<slug:slug>/', CheckInTutorialDetailView.as_view(), name='checkin-tutorial-detail'),
    path('checkin-tutorial/', CheckInTutorialListView.as_view(), name='checkin-tutorial-alias'),
    path('checkin-tutorial/<slug:slug>/', CheckInTutorialDetailView.as_view(), name='checkin-tutorial-detail-alias'),

    # Account Deletion
    path('delete-account/', account_deletion_request_view, name='delete-account-form'),
    path('delete-account-request/', AccountDeletionAPIView.as_view(), name='delete-account-request'),
    path('verify-account-deletion/<uuid:token>/', VerifyAccountDeletionView.as_view(), name='verify_account_deletion'),

    # Profile Data Deletion
    path('delete-profile-data/', delete_profile_data_request_view, name='delete-profile-data-form'),
    path('delete-profile-data-request/', ProfileDataDeletionAPIView.as_view(), name='delete-profile-data-request'),
    path('verify-profile-data-deletion/<uuid:token>/', VerifyProfileDataDeletionView.as_view(), name='verify_profile_data_deletion'),
]