from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
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

    def test_unauthenticated_request_to_send_message_returns_401(self):
        """Verify that sending a message without a Bearer token is strictly rejected with 401"""
        anonymous_client = APIClient()
        url = reverse('support_chat:send-message')
        response = anonymous_client.post(url, {"message_text": "Hello without token"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = response.json()
        self.assertFalse(data.get('success', False))

    def test_get_full_support_chat_history_api(self):
        """Verify GET /api/support-chat/messages/ returns the complete conversation and message history"""
        url = reverse('support_chat:message-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['user_email'], self.user.email)
        self.assertGreaterEqual(len(data['data']['messages']), 1)
        self.assertTrue(data['data']['messages'][0]['is_from_admin'])

    def test_user_send_text_and_video_message_api(self):
        """Verify POST /api/support-chat/send/ handles text and video/picture uploads and alerts admin"""
        url = reverse('support_chat:send-message')
        fake_video = SimpleUploadedFile("hearing_aid_issue.mp4", b"dummy_video_bytes", content_type="video/mp4")

        payload = {
            "message_text": "Here is a video of my hearing aid receiver not charging properly.",
            "attachment": fake_video
        }
        mail.outbox = []

        response = self.client.post(url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['data']['is_from_admin'])
        self.assertEqual(data['data']['message_text'], payload['message_text'])
        self.assertEqual(data['data']['attachment_type'], SupportMessage.TYPE_VIDEO)
        self.assertIsNotNone(data['data']['attachment_url'])

        # Verify conversation in database is tied to authenticated user
        conv = SupportConversation.objects.filter(user=self.user).first()
        self.assertIsNotNone(conv)
        self.assertEqual(conv.unread_admin_count, 1)

        # Verify Admin Email Notification was triggered
        self.assertGreaterEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertIn("[Care Support Alert]", sent_mail.subject)
        self.assertIn(self.user.email, sent_mail.body)

    def test_user_mark_messages_read_api(self):
        """Verify POST /api/support-chat/mark-read/ marks all admin messages as read"""
        conv = seed_default_support_chat_sample(self.user)
        conv.unread_user_count = 3
        conv.save()

        mark_url = reverse('support_chat:mark-read')
        response = self.client.post(mark_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['unread_count'], 0)

        # Verify in DB
        conv.refresh_from_db()
        self.assertEqual(conv.unread_user_count, 0)

    def test_admin_panel_form_reply_submission(self):
        """Verify that an admin replying via the Django admin changeform sends message and email"""
        from django.test import Client
        admin_web_client = Client()
        admin_web_client.force_login(self.admin_user)

        conv = SupportConversation.objects.create(
            user=self.user,
            subject="Care Consultation",
            status=SupportConversation.STATUS_OPEN,
            unread_admin_count=1
        )
        first_msg = SupportMessage.objects.create(
            conversation=conv,
            sender=self.user,
            is_from_admin=False,
            message_text="How can I pair Bluetooth?"
        )

        mail.outbox = []
        change_url = reverse('admin:support_chat_supportconversation_change', args=[conv.id])
        post_data = {
            'user': str(self.user.id),
            'subject': conv.subject,
            'status': SupportConversation.STATUS_OPEN,
            'unread_admin_count': 0,
            'unread_user_count': 0,
            'admin_reply_text': 'Press and hold the pairing button for 5 seconds until the LED flashes blue.',
            'messages-TOTAL_FORMS': '1',
            'messages-INITIAL_FORMS': '1',
            'messages-MIN_NUM_FORMS': '0',
            'messages-MAX_NUM_FORMS': '1000',
            'messages-0-id': str(first_msg.id),
            'messages-0-conversation': str(conv.id),
            'messages-0-sender': str(self.user.id),
            'messages-0-sender_name': self.user.name,
            'messages-0-message_text': 'How can I pair Bluetooth?',
            'messages-0-attachment_type': 'text',
            '_save': 'Save'
        }
        res = admin_web_client.post(change_url, post_data)
        self.assertEqual(res.status_code, 302)  # Redirect on successful save

        # Verify admin message was created
        admin_msg = conv.messages.filter(is_from_admin=True).first()
        self.assertIsNotNone(admin_msg)
        self.assertIn("LED flashes blue", admin_msg.message_text)

        # Verify email was dispatched to the client
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)