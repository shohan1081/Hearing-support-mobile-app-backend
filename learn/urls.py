from django.urls import path
from .views import TodayLessonView, WelcomeTutorialView

app_name = 'learn'

urlpatterns = [
    # Welcome Tutorial Video API
    path('welcome-tutorial/', WelcomeTutorialView.as_view(), name='welcome-tutorial'),
    path('welcome/', WelcomeTutorialView.as_view(), name='welcome-tutorial-alias'),

    # API for Today's Lesson (video & audio)
    path('', TodayLessonView.as_view(), name='learn-index'),
    path('today/', TodayLessonView.as_view(), name='today-lesson'),
]
