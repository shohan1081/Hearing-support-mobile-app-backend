from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EverydayListeningTip
from .utils import seed_default_everyday_listening_tips

User = get_user_model()


class SkillsStrategiesTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="skillsuser@example.com",
            name="Skills User",
            password="TestPassword123!"
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        seed_default_everyday_listening_tips()

    def test_everyday_listening_tips_list_api(self):
        url = reverse('skills_strategies:tip-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        self.assertEqual(len(data['data']), 5)
        
        # Verify all 5 requested tip slugs exist
        slugs = [item['slug'] for item in data['data']]
        expected_slugs = [
            "reduce-background-noise",
            "face-the-speaker",
            "take-breaks",
            "use-visual-cues",
            "ask-for-repetition",
        ]
        for expected in expected_slugs:
            self.assertIn(expected, slugs)

    def test_listening_tip_detail_by_slug_api(self):
        url = reverse('skills_strategies:tip-detail', kwargs={'lookup': 'reduce-background-noise'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['slug'], 'reduce-background-noise')
        self.assertEqual(data['data']['title'], 'Reduce Background Noise')
        self.assertIn("audio_url", data['data'])

    def test_listening_tip_detail_by_id_api(self):
        tip = EverydayListeningTip.objects.filter(slug='face-the-speaker').first()
        url = reverse('skills_strategies:tip-detail', kwargs={'lookup': str(tip.pk)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['slug'], 'face-the-speaker')
        self.assertIn("audio_url", data['data'])
