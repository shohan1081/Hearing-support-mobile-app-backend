from rest_framework import serializers
from .models import WhatNormalVideo, WhatNormalAudio


class WhatNormalVideoListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing What's Normal video titles & thumbnails
    """
    video_url = serializers.SerializerMethodField()
    video_embed_url = serializers.SerializerMethodField()
    is_youtube = serializers.SerializerMethodField()
    youtube_id = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = WhatNormalVideo
        fields = [
            'id',
            'order',
            'title',
            'subtitle',
            'video_url',
            'video_embed_url',
            'is_youtube',
            'youtube_id',
            'thumbnail',
            'duration_seconds',
            'has_video',
            'created_at',
        ]

    def get_video_url(self, obj):
        request = self.context.get('request')
        return obj.get_video_stream_url(request=request)

    def get_video_embed_url(self, obj):
        return obj.get_embed_url()

    def get_is_youtube(self, obj):
        return obj.is_youtube_video()

    def get_youtube_id(self, obj):
        return obj.get_youtube_id()

    def get_has_video(self, obj):
        return bool(obj.video_file or obj.video_url)

    def get_thumbnail(self, obj):
        request = self.context.get('request')
        return obj.get_effective_thumbnail_url(request=request)


class WhatNormalVideoDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed What's Normal video info, description, and play video URL
    """
    video_url = serializers.SerializerMethodField()
    video_embed_url = serializers.SerializerMethodField()
    is_youtube = serializers.SerializerMethodField()
    youtube_id = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = WhatNormalVideo
        fields = [
            'id',
            'order',
            'title',
            'subtitle',
            'description',
            'video_url',
            'video_embed_url',
            'is_youtube',
            'youtube_id',
            'has_video',
            'thumbnail',
            'duration_seconds',
            'created_at',
            'updated_at',
        ]

    def get_video_url(self, obj):
        request = self.context.get('request')
        return obj.get_video_stream_url(request=request)

    def get_video_embed_url(self, obj):
        return obj.get_embed_url()

    def get_is_youtube(self, obj):
        return obj.is_youtube_video()

    def get_youtube_id(self, obj):
        return obj.get_youtube_id()

    def get_has_video(self, obj):
        return bool(obj.video_file or obj.video_url)

    def get_thumbnail(self, obj):
        request = self.context.get('request')
        return obj.get_effective_thumbnail_url(request=request)


class WhatNormalAudioListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing What's Normal audio titles & thumbnails
    """
    audio_url = serializers.SerializerMethodField()
    has_audio = serializers.SerializerMethodField()

    class Meta:
        model = WhatNormalAudio
        fields = [
            'id',
            'order',
            'title',
            'subtitle',
            'audio_url',
            'thumbnail',
            'duration_seconds',
            'has_audio',
            'created_at',
        ]

    def get_audio_url(self, obj):
        request = self.context.get('request')
        return obj.get_audio_stream_url(request=request)

    def get_has_audio(self, obj):
        return bool(obj.audio_file or obj.audio_url)


class WhatNormalAudioDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed What's Normal audio info, description, and play audio URL
    """
    audio_url = serializers.SerializerMethodField()
    has_audio = serializers.SerializerMethodField()

    class Meta:
        model = WhatNormalAudio
        fields = [
            'id',
            'order',
            'title',
            'subtitle',
            'description',
            'audio_url',
            'has_audio',
            'thumbnail',
            'duration_seconds',
            'created_at',
            'updated_at',
        ]

    def get_audio_url(self, obj):
        request = self.context.get('request')
        return obj.get_audio_stream_url(request=request)

    def get_has_audio(self, obj):
        return bool(obj.audio_file or obj.audio_url)
