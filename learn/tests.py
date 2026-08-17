from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    DailyLesson,
    WelcomeTutorial,
    CheckInOverviewVideo,
    CareTeamSupportVideo,
    ProgressOverviewVideo,
    UserLessonProgress,
)
from .utils import (
    seed_default_daily_lessons,
    seed_default_welcome_tutorial,
    seed_default_checkin_overview_video,
    seed_default_care_team_support_video,
    seed_default_progress_overview_video,
    get_or_create_user_lesson_progress,
)

User = get_user_model()


class LearnAppTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="todaylearn@example.com",
            name="Today Learn User",
            password="TestPassword123!"
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        seed_default_daily_lessons()
        seed_default_welcome_tutorial()
        seed_default_checkin_overview_video()
        seed_default_care_team_support_video()
        seed_default_progress_overview_video()

    def test_welcome_tutorial_api(self):
        url = reverse('learn:welcome-tutorial')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['title'], "Welcome to Your Hearing Journey")
        self.assertIn("video_url", data['data'])

    def test_checkin_overview_video_api(self):
        url = reverse('learn:checkin-overview-video')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['title'], "Daily Check-in Overview")
        self.assertIn("video_url", data['data'])

    def test_care_team_support_video_api(self):
        url = reverse('learn:care-team-support-video')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['title'], "Care Team Support Guide")
        self.assertIn("video_url", data['data'])

    def test_progress_overview_video_api(self):
        url = reverse('learn:progress-overview-video')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['title'], "Progress Tracking Overview")
        self.assertIn("video_url", data['data'])

    def test_today_lesson_api(self):
        url = reverse('learn:today-lesson')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['current_day'], 1)
        self.assertIsNotNone(data['data']['today_lesson'])
        self.assertIn("video_url", data['data']['today_lesson'])
        self.assertIn("audio_url", data['data']['today_lesson'])

    def test_today_lesson_day_progression(self):
        progress = get_or_create_user_lesson_progress(self.user)
        # Advance user start_date by 2 days -> Day 3
        progress.start_date = timezone.now().date() - timedelta(days=2)
        progress.save()

        url = reverse('learn:today-lesson')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['current_day'], 3)
        self.assertEqual(data['data']['today_lesson']['day_number'], 3)
