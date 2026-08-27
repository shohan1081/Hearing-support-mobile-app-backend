from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
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

    def test_unauthenticated_request_to_send_message_returns_401(self):
        """Verify that sending a message without a Bearer token is strictly rejected with 401"""
        anonymous_client = APIClient()
        url = reverse('support_chat:send-message')
        response = anonymous_client.post(url, {"message_text": "Hello without token"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = response.json()
        self.assertFalse(data.get('success', False))

    def test_user_conversation_api(self):
        url = reverse('support_chat:my-conversation')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['user_email'], self.user.email)
        self.assertGreaterEqual(len(data['data']['messages']), 1)
        self.assertTrue(data['data']['messages'][0]['is_from_admin'])

    def test_user_send_message_api_and_admin_notification(self):
        url = reverse('support_chat:send-message')
        payload = {
            "message_text": "Hello Care Team, how do I clean my new Phonak hearing aid receiver?",
            "attachment_type": "text"
        }
        # Clear outbox before sending
        mail.outbox = []

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['data']['is_from_admin'])
        self.assertEqual(data['data']['message_text'], payload['message_text'])
        self.assertEqual(data['data']['sender_name'], self.user.name)

        # Verify conversation in database is tied to authenticated user
        conv = SupportConversation.objects.filter(user=self.user).first()
        self.assertIsNotNone(conv)
        self.assertEqual(conv.unread_admin_count, 1)

        # Verify Admin Email Notification was triggered
        self.assertGreaterEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertIn("[Care Support Alert]", sent_mail.subject)
        self.assertIn(self.user.email, sent_mail.body)
        self.assertIn("Phonak hearing aid", sent_mail.body)

    def test_mark_read_and_unread_count_api(self):
        conv = seed_default_support_chat_sample(self.user)
        conv.unread_user_count = 2
        conv.save()

        count_url = reverse('support_chat:unread-count')
        response = self.client.get(count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['data']['unread_count'], 2)

        mark_url = reverse('support_chat:mark-read')
        response = self.client.post(mark_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_after = self.client.get(count_url)
        self.assertEqual(response_after.json()['data']['unread_count'], 0)

    def test_admin_conversation_list_and_reply_api(self):
        send_url = reverse('support_chat:send-message')
        self.client.post(send_url, {"message_text": "I need help with volume adjustment."})

        list_url = reverse('support_chat:admin-conversations')
        response = self.admin_client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['data']), 1)

        conv_id = data['data'][0]['id']

        # Clear outbox before admin reply
        mail.outbox = []

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

        conv_updated = SupportConversation.objects.get(pk=conv_id)
        self.assertEqual(conv_updated.unread_user_count, 1)
        self.assertEqual(conv_updated.unread_admin_count, 0)

        # Verify User Email Notification was triggered
        self.assertGreaterEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertIn("Hearing Care Support: New Reply", sent_mail.subject)
        self.assertIn(self.user.email, sent_mail.to)