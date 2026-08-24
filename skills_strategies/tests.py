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

    def test_start_the_conversation_audio_api(self):
        url = reverse('skills_strategies:start-the-conversation')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['slug'], 'start-the-conversation')
        self.assertEqual(data['data']['title'], 'Start the conversation')
        self.assertIn('audio_stream_url', data['data'])
        self.assertTrue(data['data']['has_audio'])

    def test_manage_group_conversations_audio_api(self):
        url = reverse('skills_strategies:manage-group-conversations')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['slug'], 'manage-group-conversations')
        self.assertEqual(data['data']['title'], 'Manage group conversations')
        self.assertIn('audio_stream_url', data['data'])

    def test_improve_understanding_audio_api(self):
        url = reverse('skills_strategies:improve-understanding')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['slug'], 'improve-understanding')
        self.assertEqual(data['data']['title'], 'Improve understanding')
        self.assertIn('audio_stream_url', data['data'])

    def test_handle_misunderstandings_audio_api(self):
        url = reverse('skills_strategies:handle-misunderstandings')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['slug'], 'handle-misunderstandings')
        self.assertEqual(data['data']['title'], 'Handle misunderstandings')
        self.assertIn('audio_stream_url', data['data'])

    def test_build_stronger_connections_audio_api(self):
        url = reverse('skills_strategies:build-stronger-connections')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['slug'], 'build-stronger-connections')
        self.assertEqual(data['data']['title'], 'Build stronger connections')
        self.assertIn('audio_stream_url', data['data'])

    def test_all_skills_strategies_list_api(self):
        url = reverse('skills_strategies:tip-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['total_count'], 5)

        slugs = [item['slug'] for item in data['data']['sections']]
        expected_slugs = [
            "start-the-conversation",
            "manage-group-conversations",
            "improve-understanding",
            "handle-misunderstandings",
            "build-stronger-connections",
        ]
        for expected in expected_slugs:
            self.assertIn(expected, slugs)

    def test_detail_by_slug_api(self):
        url = reverse('skills_strategies:tip-detail', kwargs={'lookup': 'start-the-conversation'})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['slug'], 'start-the-conversation')
        self.assertIn("audio_stream_url", data['data'])