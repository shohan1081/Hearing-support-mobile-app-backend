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

    def test_main_overview_api(self):
        url = reverse('skills_strategies:overview')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['sections']), 4)
        section_titles = [s['title'] for s in data['data']['sections']]
        self.assertIn("Everyday Listening Tips", section_titles)
        self.assertIn("Communication Strategies", section_titles)
        self.assertIn("Building Confidence", section_titles)
        self.assertIn("Practice and Progress", section_titles)

    # ========================================================
    # 1. Everyday Listening Tips Tests (5 Audios)
    # ========================================================
    def test_everyday_listening_tips_list_api(self):
        url = reverse('skills_strategies:everyday-listening-tips-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['total_count'], 5)

    def test_everyday_listening_5_audio_endpoints(self):
        slugs = [
            'reduce-background-noise',
            'face-the-speaker',
            'take-breaks',
            'use-visual-cues',
            'ask-for-repetition',
        ]
        for slug in slugs:
            url = reverse(f'skills_strategies:{slug}')
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_200_OK, f"Failed for slug: {slug}")
            data = res.json()
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['slug'], slug)
            self.assertIn('audio_stream_url', data['data'])

    # ========================================================
    # 2. Communication Strategies Tests (5 Audios)
    # ========================================================
    def test_communication_strategies_list_api(self):
        url = reverse('skills_strategies:communication-strategies-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['total_count'], 5)

    def test_communication_strategies_5_audio_endpoints(self):
        comm_slugs = [
            ('comm-start-the-conversation', 'start-the-conversation'),
            ('comm-manage-group-conversations', 'manage-group-conversations'),
            ('comm-improve-understanding', 'improve-understanding'),
            ('comm-handle-misunderstandings', 'handle-misunderstandings'),
            ('comm-build-stronger-connections', 'build-stronger-connections'),
        ]
        for route_name, slug in comm_slugs:
            url = reverse(f'skills_strategies:{route_name}')
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_200_OK, f"Failed for route: {route_name}")
            data = res.json()
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['slug'], slug)
            self.assertIn('audio_stream_url', data['data'])

    # ========================================================
    # 3. Building Confidence Tests (5 Audios)
    # ========================================================
    def test_building_confidence_list_api(self):
        url = reverse('skills_strategies:building-confidence-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['total_count'], 5)

    def test_building_confidence_5_audio_endpoints(self):
        conf_slugs = [
            ('conf-start-small', 'start-small'),
            ('conf-prepare-before-conversations', 'prepare-before-conversations'),
            ('conf-be-patient-with-yourself', 'be-patient-with-yourself'),
            ('conf-practice-every-day', 'practice-every-day'),
            ('conf-celebrate-progress', 'celebrate-progress'),
        ]
        for route_name, slug in conf_slugs:
            url = reverse(f'skills_strategies:{route_name}')
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_200_OK, f"Failed for route: {route_name}")
            data = res.json()
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['slug'], slug)
            self.assertIn('audio_stream_url', data['data'])

    # ========================================================
    # 4. Practice and Progress Test (No audio needed)
    # ========================================================
    def test_practice_and_progress_endpoint(self):
        url = reverse('skills_strategies:practice-and-progress')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['data']['has_audio'])
        self.assertIn('recommended_actions', data['data'])