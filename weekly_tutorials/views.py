from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.authentication import FirebaseAuthentication

from .models import WeeklyTutorial, UserWeeklyProgress
from .serializers import (
    WeeklyTutorialListSerializer,
    WeeklyTutorialDetailSerializer,
    UserWeeklyProgressSerializer,
)
from .utils import get_or_create_user_progress, seed_default_weekly_tutorials


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


class CurrentWeekView(APIView):
    """
    API endpoint to fetch user's current week tutorial & banner status
    
    GET /api/weekly-tutorials/current/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_weekly_tutorials()
        user_progress = get_or_create_user_progress(request.user)
        current_week_num = user_progress.get_current_week()

        tutorial = WeeklyTutorial.objects.filter(week_number=current_week_num, is_active=True).first()

        progress_serializer = UserWeeklyProgressSerializer(user_progress)
        tutorial_serializer = (
            WeeklyTutorialDetailSerializer(tutorial, context={'request': request, 'user_progress': user_progress}).data
            if tutorial else None
        )

        return standard_response(
            success=True,
            message=f"Current week status retrieved (Week {current_week_num})",
            data={
                "current_week": current_week_num,
                "banner_message": tutorial.banner_text if tutorial else "",
                "progress": progress_serializer.data,
                "tutorial": tutorial_serializer
            },
            status_code=status.HTTP_200_OK
        )


class WeeklyTutorialListView(APIView):
    """
    API endpoint to list all 6 weekly tutorials with unlock & completion status
    
    GET /api/weekly-tutorials/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_weekly_tutorials()
        user_progress = get_or_create_user_progress(request.user)
        tutorials = WeeklyTutorial.objects.filter(is_active=True).order_by('week_number')

        serializer = WeeklyTutorialListSerializer(
            tutorials,
            many=True,
            context={'request': request, 'user_progress': user_progress}
        )

        return standard_response(
            success=True,
            message="Weekly tutorials list retrieved successfully",
            data={
                "current_week": user_progress.get_current_week(),
                "completed_weeks": user_progress.completed_weeks,
                "tutorials": serializer.data
            },
            status_code=status.HTTP_200_OK
        )


class WeeklyTutorialDetailView(APIView):
    """
    API endpoint to retrieve details of a specific week tutorial (1 to 6)
    
    GET /api/weekly-tutorials/<week_number>/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request, week_number):
        seed_default_weekly_tutorials()
        user_progress = get_or_create_user_progress(request.user)

        if week_number < 1 or week_number > 6:
            return standard_response(
                success=False,
                message="Invalid week number. Must be between 1 and 6.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        tutorial = WeeklyTutorial.objects.filter(week_number=week_number, is_active=True).first()
        if not tutorial:
            return standard_response(
                success=False,
                message=f"Tutorial for Week {week_number} not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = WeeklyTutorialDetailSerializer(
            tutorial,
            context={'request': request, 'user_progress': user_progress}
        )

        return standard_response(
            success=True,
            message=f"Week {week_number} tutorial details retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class CompleteWeekView(APIView):
    """
    API endpoint to mark a specific week as completed
    
    POST /api/weekly-tutorials/<week_number>/complete/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def post(self, request, week_number):
        if week_number < 1 or week_number > 6:
            return standard_response(
                success=False,
                message="Invalid week number. Must be between 1 and 6.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user_progress = get_or_create_user_progress(request.user)
        user_progress.mark_week_completed(week_number)

        return standard_response(
            success=True,
            message=f"Week {week_number} marked as completed successfully.",
            data={
                "current_week": user_progress.get_current_week(),
                "completed_weeks": user_progress.completed_weeks,
            },
            status_code=status.HTTP_200_OK
        )


class UpdateJourneyStartDateView(APIView):
    """
    API endpoint to update user's journey start date (e.g. for testing week progression)
    
    POST /api/weekly-tutorials/set-start-date/
    Request Body:
    {
        "journey_start_date": "2026-08-01"
    }
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def post(self, request):
        start_date_str = request.data.get('journey_start_date')
        if not start_date_str:
            return standard_response(
                success=False,
                message="journey_start_date is required (YYYY-MM-DD)",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        from datetime import datetime
        try:
            parsed_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            return standard_response(
                success=False,
                message="Invalid date format. Use YYYY-MM-DD format.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user_progress = get_or_create_user_progress(request.user)
        user_progress.journey_start_date = parsed_date
        user_progress.save(update_fields=['journey_start_date', 'updated_at'])

        return standard_response(
            success=True,
            message=f"Journey start date updated to {parsed_date}. User is now in Week {user_progress.get_current_week()}.",
            data={
                "journey_start_date": str(user_progress.journey_start_date),
                "current_week": user_progress.get_current_week(),
                "completed_weeks": user_progress.completed_weeks,
            },
            status_code=status.HTTP_200_OK
        )
