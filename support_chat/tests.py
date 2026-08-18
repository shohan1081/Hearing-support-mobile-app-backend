from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import SupportConversation, SupportMessage
from .utils import seed_default_support_chat_sample

User = get_user_model()


class SupportChatTestCase(TestCase):
    def setUp(self):
        # Create normal mobile user
        self.user = User.objects.create_user(
            email="chatuser@example.com",
            name="Chat Mobile User",
            password="TestPassword123!"
        )
        self.client = APIClient()
        refresh_user = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_user.access_token}')

        # Create Care Team Admin user
        self.admin_user = User.objects.create_superuser(
            email="admincare@example.com",
            name="Care Team Admin Specialist",
            password="AdminPassword123!"
        )
        self.admin_client = APIClient()
        refresh_admin = RefreshToken.for_user(self.admin_user)
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_admin.access_token}')

    def test_user_conversation_api(self):
        url = reverse('support_chat:my-conversation')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['user_email'], self.user.email)
        self.assertGreaterEqual(len(data['data']['messages']), 1)
        self.assertTrue(data['data']['messages'][0]['is_from_admin'])

    def test_user_send_message_api(self):
        url = reverse('support_chat:send-message')
        payload = {
            "message_text": "Hello Care Team, how do I clean my new Phonak hearing aid receiver?",
            "attachment_type": "text"
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['data']['is_from_admin'])
        self.assertEqual(data['data']['message_text'], payload['message_text'])

        # Verify conversation updated
        conv = SupportConversation.objects.filter(user=self.user).first()
        self.assertEqual(conv.unread_admin_count, 1)

    def test_mark_read_and_unread_count_api(self):
        # Care team admin replies to user
        conv = seed_default_support_chat_sample(self.user)
        conv.unread_user_count = 2
        conv.save()

        # Check unread count API
        count_url = reverse('support_chat:unread-count')
        response = self.client.get(count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['data']['unread_count'], 2)

        # Mark read API
        mark_url = reverse('support_chat:mark-read')
        response = self.client.post(mark_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check unread count after marking read
        response_after = self.client.get(count_url)
        self.assertEqual(response_after.json()['data']['unread_count'], 0)

    def test_admin_conversation_list_and_reply_api(self):
        # Send user message
        send_url = reverse('support_chat:send-message')
        self.client.post(send_url, {"message_text": "I need help with volume adjustment."})

        # Admin lists all conversations
        list_url = reverse('support_chat:admin-conversations')
        response = self.admin_client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['data']), 1)

        conv_id = data['data'][0]['id']

        # Admin replies to user
        reply_url = reverse('support_chat:admin-reply')
        reply_payload = {
            "conversation_id": conv_id,
            "message_text": "Hello! You can adjust the volume via the app home slider or on the side button."
        }
        reply_res = self.admin_client.post(reply_url, reply_payload)
        self.assertEqual(reply_res.status_code, status.HTTP_201_CREATED)
        reply_data = reply_res.json()
        self.assertTrue(reply_data['success'])
        self.assertTrue(reply_data['data']['is_from_admin'])

        # Verify user now has 1 unread message from admin
        conv_updated = SupportConversation.objects.get(pk=conv_id)
        self.assertEqual(conv_updated.unread_user_count, 1)
        self.assertEqual(conv_updated.unread_admin_count, 0)
