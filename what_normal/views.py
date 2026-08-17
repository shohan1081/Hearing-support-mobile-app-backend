from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.authentication import FirebaseAuthentication

from .models import WhatNormalVideo, WhatNormalAudio
from .serializers import (
    WhatNormalVideoListSerializer,
    WhatNormalVideoDetailSerializer,
    WhatNormalAudioListSerializer,
    WhatNormalAudioDetailSerializer,
)
from .utils import seed_default_what_normal_media


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


class WhatNormalVideoListView(APIView):
    """
    API endpoint to get list of all 'What's Normal' video titles & thumbnails
    
    GET /api/what-normal/videos/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_what_normal_media()
        videos = WhatNormalVideo.objects.filter(is_active=True).order_by('order', 'created_at')
        serializer = WhatNormalVideoListSerializer(videos, many=True, context={'request': request})
        return standard_response(
            success=True,
            message="What's Normal video list retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class WhatNormalVideoDetailView(APIView):
    """
    API endpoint to get detail view for a specific 'What's Normal' video (video_url, description, thumbnail)
    
    GET /api/what-normal/videos/<id>/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request, pk):
        seed_default_what_normal_media()
        try:
            video = WhatNormalVideo.objects.get(pk=pk, is_active=True)
        except WhatNormalVideo.DoesNotExist:
            return standard_response(
                success=False,
                message="Video not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = WhatNormalVideoDetailSerializer(video, context={'request': request})
        return standard_response(
            success=True,
            message="Video details retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class WhatNormalAudioListView(APIView):
    """
    API endpoint to get list of all 'What's Normal' audio tracks & thumbnails
    
    GET /api/what-normal/audios/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_what_normal_media()
        audios = WhatNormalAudio.objects.filter(is_active=True).order_by('order', 'created_at')
        serializer = WhatNormalAudioListSerializer(audios, many=True, context={'request': request})
        return standard_response(
            success=True,
            message="What's Normal audio list retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class WhatNormalAudioDetailView(APIView):
    """
    API endpoint to play audio and get detailed audio info (audio_url, description, thumbnail)
    
    GET /api/what-normal/audios/<id>/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request, pk):
        seed_default_what_normal_media()
        try:
            audio = WhatNormalAudio.objects.get(pk=pk, is_active=True)
        except WhatNormalAudio.DoesNotExist:
            return standard_response(
                success=False,
                message="Audio track not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = WhatNormalAudioDetailSerializer(audio, context={'request': request})
        return standard_response(
            success=True,
            message="Audio track details retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
