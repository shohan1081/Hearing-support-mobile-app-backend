from django.urls import path
from .views import (
    CurrentWeekView,
    WeeklyTutorialListView,
    WeeklyTutorialDetailView,
    CompleteWeekView,
    UpdateJourneyStartDateView,
)

app_name = 'weekly_tutorials'

urlpatterns = [
    # Current week banner & status for logged-in user
    path('current/', CurrentWeekView.as_view(), name='current-week'),

    # List all 6 weeks with status
    path('', WeeklyTutorialListView.as_view(), name='tutorial-list'),

    # Tutorial detail for a specific week number (1 to 6)
    path('<int:week_number>/', WeeklyTutorialDetailView.as_view(), name='tutorial-detail'),

    # Mark a week as completed
    path('<int:week_number>/complete/', CompleteWeekView.as_view(), name='complete-week'),

    # Update journey start date (useful for testing or resetting week progression)
    path('set-start-date/', UpdateJourneyStartDateView.as_view(), name='set-start-date'),
]
