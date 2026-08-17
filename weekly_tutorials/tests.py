from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import WeeklyTutorial, UserWeeklyProgress
from .utils import seed_default_weekly_tutorials, get_or_create_user_progress

User = get_user_model()


class WeeklyTutorialsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            name="Test User",
            password="TestPassword123!"
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        seed_default_weekly_tutorials()

    def test_seed_default_weekly_tutorials(self):
        self.assertEqual(WeeklyTutorial.objects.count(), 6)
        week1 = WeeklyTutorial.objects.get(week_number=1)
        self.assertIn("week 1: Awareness", week1.banner_text)
        week2 = WeeklyTutorial.objects.get(week_number=2)
        self.assertIn("week 2: Adjustment", week2.banner_text)

    def test_user_weekly_progress_calculation(self):
        progress = get_or_create_user_progress(self.user)
        self.assertEqual(progress.get_current_week(), 1)

        # Set journey start date to 10 days ago -> Week 2
        progress.journey_start_date = timezone.now().date() - timedelta(days=10)
        progress.save()
        self.assertEqual(progress.get_current_week(), 2)

        # Set journey start date to 40 days ago -> Week 6 (capped at 6)
        progress.journey_start_date = timezone.now().date() - timedelta(days=40)
        progress.save()
        self.assertEqual(progress.get_current_week(), 6)

    def test_current_week_api(self):
        url = reverse('weekly_tutorials:current-week')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['current_week'], 1)
        self.assertIn("week 1: Awareness", data['data']['banner_message'])

    def test_weekly_tutorial_list_api(self):
        url = reverse('weekly_tutorials:tutorial-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['tutorials']), 6)

    def test_weekly_tutorial_detail_api(self):
        url = reverse('weekly_tutorials:tutorial-detail', kwargs={'week_number': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['week_number'], 1)
        self.assertEqual(data['data']['title'], "Awareness")
        self.assertIsInstance(data['data']['what_you_will_learn'], list)

        url_w2 = reverse('weekly_tutorials:tutorial-detail', kwargs={'week_number': 2})
        response_w2 = self.client.get(url_w2)
        self.assertEqual(response_w2.status_code, status.HTTP_200_OK)
        data_w2 = response_w2.json()
        self.assertIn("week 2: Adjustment", data_w2['data']['banner_text'])

    def test_complete_week_api(self):
        url = reverse('weekly_tutorials:complete-week', kwargs={'week_number': 1})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn(1, data['data']['completed_weeks'])

    def test_update_journey_start_date_api(self):
        url = reverse('weekly_tutorials:set-start-date')
        past_date = (timezone.now().date() - timedelta(days=14)).strftime("%Y-%m-%d")
        response = self.client.post(url, {"journey_start_date": past_date}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['current_week'], 3)
