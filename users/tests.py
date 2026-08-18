from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import HearingAidWearTime, DailyCheckIn

User = get_user_model()


class WearTimeAndHearingScoreTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="weartimeuser@example.com",
            name="Wear Time User",
            password="TestPassword123!"
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_log_wear_time_api(self):
        url = reverse('users:wear-time')
        payload = {
            "hours": 8,
            "minutes": 30,
            "notes": "Wore machine during work and evening family time."
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['hours'], 8)
        self.assertEqual(data['data']['minutes'], 30)
        self.assertEqual(data['data']['total_minutes'], 510)
        self.assertEqual(data['data']['total_hours'], 8.5)

    def test_get_wear_time_api(self):
        # Create wear time logs
        HearingAidWearTime.objects.create(
            user=self.user,
            date=timezone.now().date(),
            hours=7,
            minutes=45,
            notes="Daily usage"
        )
        url = reverse('users:wear-time')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['data']['today_wear_time'])
        self.assertEqual(data['data']['today_wear_time']['hours'], 7)
        self.assertGreater(data['data']['weekly_average_hours'], 0)

    def test_get_hearing_score_api(self):
        # Log wear time and check-in to boost real score
        HearingAidWearTime.objects.create(
            user=self.user,
            date=timezone.now().date(),
            hours=9,
            minutes=0
        )
        DailyCheckIn.objects.create(
            user=self.user,
            hearing_status="great",
            what_went_well="Speech was clear",
            checkin_date=timezone.now().date()
        )

        url = reverse('users:hearing-score')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        score = data['data']['hearing_score']
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 1)
        self.assertLessEqual(score, 100)
        self.assertIn('status', data['data'])
        self.assertIn('acknowledgment', data['data'])
        self.assertIn(data['data']['status'], ['Excellent', 'Good', 'Average', 'Poor', 'Bad'])
