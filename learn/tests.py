from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import DailyLesson, WelcomeTutorial, UserLessonProgress
from .utils import seed_default_daily_lessons, seed_default_welcome_tutorial, get_or_create_user_lesson_progress

User = get_user_model()


class LearnTodayLessonTestCase(TestCase):
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

    def test_welcome_tutorial_api(self):
        url = reverse('learn:welcome-tutorial')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['title'], "Welcome to Your Hearing Journey")
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
