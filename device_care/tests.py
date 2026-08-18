from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import HearingAidBrand, HearingAidModel, DeviceCareSection, DeviceCareVideo
from .utils import seed_default_device_care_data

User = get_user_model()


class DeviceCareTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="devicecare@example.com",
            name="Device Care User",
            password="TestPassword123!"
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        seed_default_device_care_data()

    def test_brand_list_api(self):
        url = reverse('device_care:brand-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        self.assertGreaterEqual(len(data['data']), 2)
        brand_names = [b['name'] for b in data['data']]
        self.assertIn("Phonak", brand_names)
        self.assertIn("Oticon", brand_names)

    def test_brand_detail_api(self):
        url = reverse('device_care:brand-detail', kwargs={'lookup': 'phonak'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['slug'], 'phonak')
        self.assertEqual(data['data']['name'], 'Phonak')
        self.assertGreaterEqual(len(data['data']['models']), 1)
        self.assertEqual(data['data']['models'][0]['name'], 'Audéo Lumity')

    def test_model_list_api(self):
        url = reverse('device_care:model-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        model_names = [m['name'] for m in data['data']]
        self.assertIn("Audéo Lumity", model_names)

    def test_model_detail_api(self):
        url = reverse('device_care:model-detail', kwargs={'lookup': 'audeo-lumity'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['slug'], 'audeo-lumity')
        self.assertEqual(data['data']['user_manual_url'], 'https://www.phonak.com/en-us/support/user-guides')
        
        # Verify 4 care sections exist (cleaning_guide, care_tips, troubleshooting, user_manual)
        sections = data['data']['sections']
        self.assertGreaterEqual(len(sections), 4)
        section_types = [s['section_type'] for s in sections]
        self.assertIn('cleaning_guide', section_types)
        self.assertIn('care_tips', section_types)
        self.assertIn('troubleshooting', section_types)
        self.assertIn('user_manual', section_types)

        # Verify cleaning_guide has nested videos
        cleaning_sec = next(s for s in sections if s['section_type'] == 'cleaning_guide')
        self.assertGreaterEqual(len(cleaning_sec['videos']), 1)
        self.assertIn('video_url', cleaning_sec['videos'][0])

    def test_section_detail_api(self):
        section = DeviceCareSection.objects.filter(section_type='cleaning_guide').first()
        url = reverse('device_care:section-detail', kwargs={'pk': section.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['id'], section.pk)
        self.assertIn("content_text", data['data'])
        self.assertIn("videos", data['data'])
