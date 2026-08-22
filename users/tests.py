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

    def test_today_wear_time_api(self):
        HearingAidWearTime.objects.create(
            user=self.user,
            date=timezone.now().date(),
            hours=7,
            minutes=30
        )
        url = reverse('users:today-wear-time')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['hours_worn'], 7)
        self.assertEqual(data['data']['minutes_worn'], 30)
        self.assertEqual(data['data']['total_hours'], 7.5)
        self.assertEqual(data['data']['daily_goal_hours'], 8)
        self.assertEqual(data['data']['goal_completion_percentage'], 93.8)

    def test_daily_activity_score_api(self):
        HearingAidWearTime.objects.create(
            user=self.user,
            date=timezone.now().date(),
            hours=8,
            minutes=0
        )
        DailyCheckIn.objects.create(
            user=self.user,
            hearing_status="great",
            what_went_well="Good sound quality",
            checkin_date=timezone.now().date()
        )
        url = reverse('users:daily-activity-score')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        activity_score = data['data']['activity_score']
        self.assertIsInstance(activity_score, int)
        self.assertGreaterEqual(activity_score, 1)
        self.assertLessEqual(activity_score, 5)

    def test_progress_chart_monthly_api(self):
        url = reverse('users:progress-chart') + '?period=monthly'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['period'], 'monthly')
        self.assertIn('chart_data', data['data'])
        self.assertGreater(len(data['data']['chart_data']), 25)

    def test_progress_chart_yearly_api(self):
        url = reverse('users:progress-chart') + '?period=yearly'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['period'], 'yearly')
        self.assertEqual(len(data['data']['chart_data']), 12)

    def test_user_wear_goal_api(self):
        url = reverse('users:wear-goal')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['data']['daily_wear_goal_hours'], 8)

        # Update goal to 10 hours
        update_response = self.client.put(url, {"daily_wear_goal_hours": 10}, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.json()['data']['daily_wear_goal_hours'], 10)

    def test_consistency_report_weekly_api(self):
        HearingAidWearTime.objects.create(
            user=self.user,
            date=timezone.now().date(),
            hours=8,
            minutes=30
        )
        url = reverse('users:consistency-report') + '?period=weekly'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['period'], 'weekly')
        self.assertEqual(len(data['data']['bar_chart_data']), 7)
        self.assertIn('wear_hours', data['data']['bar_chart_data'][0])
        self.assertIn('goal_hours', data['data']['bar_chart_data'][0])

    def test_consistency_report_monthly_api(self):
        url = reverse('users:consistency-report') + '?period=monthly'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['period'], 'monthly')
        self.assertGreaterEqual(len(data['data']['bar_chart_data']), 4)
        self.assertIn('average_daily_wear_hours', data['data']['bar_chart_data'][0])
        self.assertIn('daily_goal_hours', data['data']['bar_chart_data'][0])


class AppointmentAndStrugglingCheckInTestCase(TestCase):
    def setUp(self):
        from .models import Appointment
        self.Appointment = Appointment
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="patient@example.com",
            name="Jane Patient",
            password="TestPassword123!"
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_struggling_checkin_and_appointment_flow(self):
        # 1. User submits struggling daily check-in
        checkin_url = reverse('users:daily-checkin')
        checkin_payload = {
            "hearing_status": "struggling",
            "why_struggling": "Background noise in restaurant was way too sharp."
        }
        res = self.client.post(checkin_url, checkin_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        checkin_id = res.json()['data']['id']
        checkin_obj = DailyCheckIn.objects.get(id=checkin_id)

        # 2. Check checkin GET initially has no appointment
        get_res = self.client.get(checkin_url)
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertFalse(get_res.json()['data']['has_upcoming_appointment'])
        self.assertIsNone(get_res.json()['data']['upcoming_appointment'])

        # 3. Admin creates an appointment for this struggling patient
        import datetime
        tomorrow = timezone.now().date() + datetime.timedelta(days=1)
        appt = self.Appointment.objects.create(
            user=self.user,
            checkin=checkin_obj,
            title="Care Team Audiologist Consultation - Struggling",
            specialist_name="Dr. Sarah Jenkins, Au.D.",
            appointment_date=tomorrow,
            appointment_time=datetime.time(10, 30),
            duration_minutes=45,
            status=self.Appointment.STATUS_SCHEDULED,
            meeting_link="https://meet.google.com/test-care-link",
            location="Online Video Consultation",
            notes="Please have your hearing aids in your ears during this consultation."
        )

        # 4. User calls checkin API again and now sees the upcoming appointment
        get_res_after = self.client.get(checkin_url)
        self.assertEqual(get_res_after.status_code, status.HTTP_200_OK)
        self.assertTrue(get_res_after.json()['data']['has_upcoming_appointment'])
        self.assertIsNotNone(get_res_after.json()['data']['upcoming_appointment'])
        self.assertEqual(get_res_after.json()['data']['upcoming_appointment']['specialist_name'], "Dr. Sarah Jenkins, Au.D.")
        self.assertEqual(get_res_after.json()['data']['upcoming_appointment']['meeting_link'], "https://meet.google.com/test-care-link")

        # 5. User fetches appointments list
        appts_url = reverse('users:user-appointments-list')
        list_res = self.client.get(appts_url)
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        list_data = list_res.json()['data']
        self.assertEqual(list_data['total_count'], 1)
        self.assertEqual(list_data['upcoming_count'], 1)
        self.assertEqual(len(list_data['appointments']), 1)
        self.assertEqual(list_data['appointments'][0]['related_checkin']['id'], checkin_id)

        # 6. User fetches single upcoming appointment
        upcoming_url = reverse('users:user-upcoming-appointment')
        upcoming_res = self.client.get(upcoming_url)
        self.assertEqual(upcoming_res.status_code, status.HTTP_200_OK)
        self.assertTrue(upcoming_res.json()['data']['has_upcoming_appointment'])
        self.assertEqual(upcoming_res.json()['data']['appointment']['id'], appt.id)

        # 7. User fetches appointment details
        detail_url = reverse('users:user-appointment-detail', kwargs={'pk': appt.id})
        detail_res = self.client.get(detail_url)
        self.assertEqual(detail_res.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_res.json()['data']['id'], appt.id)
        self.assertEqual(detail_res.json()['data']['title'], "Care Team Audiologist Consultation - Struggling")
        self.assertTrue(detail_res.json()['data']['is_upcoming'])
