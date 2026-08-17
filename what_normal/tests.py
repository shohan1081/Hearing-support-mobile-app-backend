from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import WhatNormalVideo, WhatNormalAudio
from .utils import seed_default_what_normal_media

User = get_user_model()


class WhatNormalTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="whatnormal@example.com",
            name="What Normal User",
            password="TestPassword123!"
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        seed_default_what_normal_media()

    def test_video_list_api(self):
        url = reverse('what_normal:video-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        self.assertGreaterEqual(len(data['data']), 1)
        video_item = data['data'][0]
        self.assertIn("title", video_item)
        self.assertIn("has_video", video_item)

    def test_video_detail_api(self):
        video = WhatNormalVideo.objects.first()
        url = reverse('what_normal:video-detail', kwargs={'pk': video.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['id'], video.pk)
        self.assertEqual(data['data']['title'], video.title)
        self.assertIn("video_url", data['data'])
        self.assertIn("description", data['data'])

    def test_audio_list_api(self):
        url = reverse('what_normal:audio-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        self.assertGreaterEqual(len(data['data']), 1)
        audio_item = data['data'][0]
        self.assertIn("title", audio_item)
        self.assertIn("has_audio", audio_item)

    def test_audio_detail_api(self):
        audio = WhatNormalAudio.objects.first()
        url = reverse('what_normal:audio-detail', kwargs={'pk': audio.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['id'], audio.pk)
        self.assertEqual(data['data']['title'], audio.title)
        self.assertIn("audio_url", data['data'])
        self.assertIn("description", data['data'])
