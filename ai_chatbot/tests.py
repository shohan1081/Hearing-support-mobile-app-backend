from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AIChatSession, AIChatMessage, QuickPromptSuggestion
from .services import build_user_hearing_context, generate_smart_fallback_response, get_ai_system_prompt
from users.models import HearingAidWearTime, DailyCheckIn

User = get_user_model()


class AIChatbotTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='chatbotuser@example.com',
            password='TestPassword123!',
            name='Arthur Pendelton'
        )
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Add some wear time and daily checkin
        HearingAidWearTime.objects.create(
            user=self.user,
            date=timezone.now().date(),
            hours=6,
            minutes=30,
            notes="Morning walks and work meetings"
        )
        DailyCheckIn.objects.create(
            user=self.user,
            checkin_date=timezone.now().date(),
            hearing_status='good',
            what_went_well="Enjoyed speech clarity during breakfast"
        )

    def test_quick_prompt_suggestions_api(self):
        url = reverse('ai_chatbot:suggestions')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['data']['total_count'], 4)
        titles = [s['title'] for s in data['data']['suggestions']]
        self.assertIn("Improve Hearing Score", titles)
        self.assertIn("Noisy Environments", titles)
        self.assertIn("Struggling with Tinnitus", titles)

    def test_user_hearing_context_builder(self):
        context = build_user_hearing_context(self.user)
        self.assertEqual(context['user_name'], 'Arthur Pendelton')
        self.assertEqual(context['today_wear_hours'], 6.5)
        self.assertEqual(context['latest_checkin_status'], 'good')
        self.assertGreaterEqual(context['hearing_score'], 0)

        prompt = get_ai_system_prompt(context)
        self.assertIn('Arthur Pendelton', prompt)
        self.assertIn('6.5 hours', prompt)

    def test_smart_fallback_responses(self):
        ctx = build_user_hearing_context(self.user)

        # Test Hearing Score question
        resp1 = generate_smart_fallback_response("How can I improve my hearing score?", ctx)
        self.assertIn("Hearing Score", resp1)
        self.assertIn("Consistent Daily Wear", resp1)

        # Test Noisy environment question
        resp2 = generate_smart_fallback_response("What exercises help with noisy environments?", ctx)
        self.assertIn("Strategic Seating", resp2)
        self.assertIn("Directional Microphone", resp2)

        # Test Tinnitus question
        resp3 = generate_smart_fallback_response("I'm struggling with tinnitus today. What should I do?", ctx)
        self.assertIn("Sound Enrichment", resp3)
        self.assertIn("Deep Breathing", resp3)

        # Test Progress question
        resp4 = generate_smart_fallback_response("Tell me about my progress and wear time.", ctx)
        self.assertIn("Arthur Pendelton", resp4)
        self.assertIn("6.5 hours", resp4)

    def test_send_chat_message_endpoint(self):
        url = reverse('ai_chatbot:chat')
        payload = {
            "message": "How can I improve my hearing score?"
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('session_id', data['data'])
        self.assertIn('ai_response', data['data'])
        self.assertEqual(data['data']['user_message'], "How can I improve my hearing score?")
        self.assertIsNotNone(data['data']['user_stats_snapshot'])
        self.assertEqual(data['data']['user_stats_snapshot']['today_wear_time_hours'], 6.5)

        session_id = data['data']['session_id']

        # Multi-turn conversation continuation
        second_payload = {
            "message": "What exercises help with noisy environments?",
            "session_id": session_id
        }
        res2 = self.client.post(url, second_payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.json()['data']['session_id'], session_id)

        # Verify messages stored in DB
        session = AIChatSession.objects.get(session_id=session_id)
        self.assertEqual(session.messages.count(), 4)  # 2 user messages + 2 AI messages

    def test_list_and_detail_chat_sessions(self):
        # Create a session with message
        url = reverse('ai_chatbot:chat')
        res = self.client.post(url, {"message": "I'm struggling with tinnitus today."}, format='json')
        session_id = res.json()['data']['session_id']

        # List sessions
        list_url = reverse('ai_chatbot:session-list')
        list_res = self.client.get(list_url)
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(list_res.json()['data']['total_count'], 1)

        # Get session detail
        detail_url = reverse('ai_chatbot:session-detail', kwargs={'session_id': session_id})
        detail_res = self.client.get(detail_url)
        self.assertEqual(detail_res.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_res.json()['data']['session_id'], session_id)
        self.assertGreaterEqual(len(detail_res.json()['data']['messages']), 2)

        # Delete session
        delete_res = self.client.delete(detail_url)
        self.assertEqual(delete_res.status_code, status.HTTP_200_OK)
        self.assertEqual(AIChatSession.objects.filter(session_id=session_id).count(), 0)

    def test_clear_chat_history_endpoint(self):
        url = reverse('ai_chatbot:chat')
        self.client.post(url, {"message": "Hello AI"}, format='json')
        self.client.post(url, {"message": "Tell me about my progress"}, format='json')

        self.assertGreater(AIChatSession.objects.filter(user=self.user).count(), 0)

        clear_url = reverse('ai_chatbot:clear')
        clear_res = self.client.post(clear_url, {}, format='json')
        self.assertEqual(clear_res.status_code, status.HTTP_200_OK)
        self.assertEqual(AIChatSession.objects.filter(user=self.user).count(), 0)