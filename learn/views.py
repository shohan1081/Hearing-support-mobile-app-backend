from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.authentication import FirebaseAuthentication

from .models import (
    DailyLesson,
    WelcomeTutorial,
    CheckInOverviewVideo,
    CareTeamSupportVideo,
    ProgressOverviewVideo,
)
from .serializers import (
    DailyLessonSerializer,
    WelcomeTutorialSerializer,
    CheckInOverviewVideoSerializer,
    CareTeamSupportVideoSerializer,
    ProgressOverviewVideoSerializer,
    UserLessonProgressSerializer,
)
from .utils import (
    get_or_create_user_lesson_progress,
    seed_default_daily_lessons,
    seed_default_welcome_tutorial,
    seed_default_checkin_overview_video,
    seed_default_care_team_support_video,
    seed_default_progress_overview_video,
)


def standard_response(success=True, message="", data=None, errors=None, status_code=status.HTTP_200_OK):
    """
    Create standardized API response for consistency across the application
    """
    response_data = {
        'success': success,
        'message': message,
    }
    if data is not None:
        response_data['data'] = data
    if errors is not None:
        response_data['errors'] = errors
    return Response(response_data, status=status_code)


class WelcomeTutorialView(APIView):
    """
    API endpoint to fetch Welcome Tutorial Video for introducing users to the learning program
    
    GET /api/learn/welcome-tutorial/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_welcome_tutorial()
        welcome_tutorial = WelcomeTutorial.objects.filter(is_active=True).first()

        if not welcome_tutorial:
            return standard_response(
                success=False,
                message="Welcome tutorial video not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = WelcomeTutorialSerializer(welcome_tutorial, context={'request': request})
        return standard_response(
            success=True,
            message="Welcome tutorial video retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class CheckInOverviewVideoView(APIView):
    """
    API endpoint to fetch Check-in Overview Video
    
    GET /api/learn/checkin-overview-video/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_checkin_overview_video()
        video = CheckInOverviewVideo.objects.filter(is_active=True).first()

        if not video:
            return standard_response(
                success=False,
                message="Check-in overview video not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = CheckInOverviewVideoSerializer(video, context={'request': request})
        return standard_response(
            success=True,
            message="Check-in overview video retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class CareTeamSupportVideoView(APIView):
    """
    API endpoint to fetch Care Team Support Video
    
    GET /api/learn/care-team-support-video/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_care_team_support_video()
        video = CareTeamSupportVideo.objects.filter(is_active=True).first()

        if not video:
            return standard_response(
                success=False,
                message="Care team support video not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = CareTeamSupportVideoSerializer(video, context={'request': request})
        return standard_response(
            success=True,
            message="Care team support video retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class ProgressOverviewVideoView(APIView):
    """
    API endpoint to fetch Progress Overview Video
    
    GET /api/learn/progress-overview-video/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_progress_overview_video()
        video = ProgressOverviewVideo.objects.filter(is_active=True).first()

        if not video:
            return standard_response(
                success=False,
                message="Progress overview video not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = ProgressOverviewVideoSerializer(video, context={'request': request})
        return standard_response(
            success=True,
            message="Progress overview video retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class TodayLessonView(APIView):
    """
    API endpoint to fetch Today's Lesson (video & audio) for the logged-in user
    Lessons unlock sequentially day by day based on user's registration/start date
    
    GET /api/learn/today/
    GET /api/learn/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_daily_lessons()
        user_progress = get_or_create_user_lesson_progress(request.user)
        current_day_num = user_progress.get_current_day()

        # Try to find lesson for exact current day
        lesson = DailyLesson.objects.filter(day_number=current_day_num, is_active=True).first()

        # Fallback to highest available active lesson if current day's lesson is not yet uploaded
        if not lesson:
            lesson = DailyLesson.objects.filter(day_number__lte=current_day_num, is_active=True).order_by('-day_number').first()

        progress_serializer = UserLessonProgressSerializer(user_progress)
        lesson_serializer = (
            DailyLessonSerializer(lesson, context={'request': request}).data
            if lesson else None
        )

        return standard_response(
            success=True,
            message=f"Today's lesson retrieved (Day {current_day_num})",
            data={
                "current_day": current_day_num,
                "progress": progress_serializer.data,
                "today_lesson": lesson_serializer
            },
            status_code=status.HTTP_200_OK
        )


class AllVideoPlaylistsView(APIView):
    """
    Consolidated API endpoint to fetch all video playlists and tutorial videos across the application in one single call.
    Includes Overview Videos, Daily Lessons playlist, What's Normal video playlist, Device Care tutorial videos, and Weekly program tutorials.

    GET /api/learn/video-playlists/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        # 1. Seed defaults to ensure DB is populated
        seed_default_welcome_tutorial()
        seed_default_checkin_overview_video()
        seed_default_care_team_support_video()
        seed_default_progress_overview_video()
        seed_default_daily_lessons()

        # 2. Fetch Overview Videos
        welcome_tutorial = WelcomeTutorial.objects.filter(is_active=True).first()
        checkin_video = CheckInOverviewVideo.objects.filter(is_active=True).first()
        care_team_video = CareTeamSupportVideo.objects.filter(is_active=True).first()
        progress_video = ProgressOverviewVideo.objects.filter(is_active=True).first()

        # 3. Fetch Daily Lessons Playlist
        daily_lessons = DailyLesson.objects.filter(is_active=True).exclude(video_file="").order_by('day_number')

        # 4. Fetch What's Normal Video Playlist
        from what_normal.models import WhatNormalVideo
        from what_normal.serializers import WhatNormalVideoListSerializer
        whats_normal_videos = WhatNormalVideo.objects.filter(is_active=True).order_by('order', 'created_at')

        # 5. Fetch Device Care Tutorial Videos
        from device_care.models import DeviceCareVideo
        from device_care.serializers import DeviceCareVideoSerializer
        device_care_videos = DeviceCareVideo.objects.filter(is_active=True).order_by('order', 'created_at')

        # 6. Fetch Weekly Program Tutorials Playlist
        from weekly_tutorials.models import WeeklyTutorial
        from weekly_tutorials.serializers import WeeklyTutorialListSerializer
        weekly_tutorials = WeeklyTutorial.objects.filter(is_active=True).order_by('week_number')

        data = {
            "overview_videos": {
                "welcome_tutorial": WelcomeTutorialSerializer(welcome_tutorial, context={'request': request}).data if welcome_tutorial else None,
                "checkin_overview": CheckInOverviewVideoSerializer(checkin_video, context={'request': request}).data if checkin_video else None,
                "care_team_support": CareTeamSupportVideoSerializer(care_team_video, context={'request': request}).data if care_team_video else None,
                "progress_overview": ProgressOverviewVideoSerializer(progress_video, context={'request': request}).data if progress_video else None,
            },
            "daily_lessons_playlist": DailyLessonSerializer(daily_lessons, many=True, context={'request': request}).data,
            "whats_normal_playlist": WhatNormalVideoListSerializer(whats_normal_videos, many=True, context={'request': request}).data,
            "device_care_tutorials_playlist": DeviceCareVideoSerializer(device_care_videos, many=True, context={'request': request}).data,
            "weekly_tutorials_playlist": WeeklyTutorialListSerializer(weekly_tutorials, many=True, context={'request': request}).data,
        }

        return standard_response(
            success=True,
            message="All video playlists retrieved successfully",
            data=data,
            status_code=status.HTTP_200_OK
        )
