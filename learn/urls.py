from django.urls import path
from .views import (
    TodayLessonView,
    WelcomeTutorialView,
    CheckInOverviewVideoView,
    CareTeamSupportVideoView,
    ProgressOverviewVideoView,
)

app_name = 'learn'

urlpatterns = [
    # Welcome Tutorial Video API
    path('welcome-tutorial/', WelcomeTutorialView.as_view(), name='welcome-tutorial'),
    path('welcome/', WelcomeTutorialView.as_view(), name='welcome-tutorial-alias'),

    # Check-in Overview Video API
    path('checkin-overview-video/', CheckInOverviewVideoView.as_view(), name='checkin-overview-video'),
    path('checkin-overview/', CheckInOverviewVideoView.as_view(), name='checkin-overview-video-alias'),

    # Care Team Support Video API
    path('care-team-support-video/', CareTeamSupportVideoView.as_view(), name='care-team-support-video'),
    path('care-team-support/', CareTeamSupportVideoView.as_view(), name='care-team-support-video-alias'),

    # Progress Overview Video API
    path('progress-overview-video/', ProgressOverviewVideoView.as_view(), name='progress-overview-video'),
    path('progress-overview/', ProgressOverviewVideoView.as_view(), name='progress-overview-video-alias'),

    # API for Today's Lesson (video & audio)
    path('', TodayLessonView.as_view(), name='learn-index'),
    path('today/', TodayLessonView.as_view(), name='today-lesson'),
]
