from django.urls import path
from .views import TodayLessonView

app_name = 'learn'

urlpatterns = [
    # API for Today's Lesson (video & audio)
    path('', TodayLessonView.as_view(), name='learn-index'),
    path('today/', TodayLessonView.as_view(), name='today-lesson'),
]
