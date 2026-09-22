from rest_framework import serializers
from .models import (
    DailyLesson,
    WelcomeTutorial,
    CheckInOverviewVideo,
    CareTeamSupportVideo,
    ProgressOverviewVideo,
    UserLessonProgress,
)


class DailyLessonSerializer(serializers.ModelSerializer):
    """
    Serializer for Today's Lesson (video and audio content)
    Supports both uploaded video file and external Video URL / YouTube link.
    """
    video_url = serializers.SerializerMethodField()
    video_embed_url = serializers.SerializerMethodField()
    is_youtube = serializers.SerializerMethodField()
    youtube_id = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    audio_url = serializers.SerializerMethodField()
    has_audio = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = DailyLesson
        fields = [
            'id',
            'day_number',
            'title',
            'subtitle',
            'description',
            'video_url',
            'video_embed_url',
            'is_youtube',
            'youtube_id',
            'has_video',
            'audio_url',
            'has_audio',
            'thumbnail',
            'duration_seconds',
            'key_takeaways',
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

    def get_audio_url(self, obj):
        request = self.context.get('request')
        return obj.get_audio_stream_url(request=request)

    def get_has_audio(self, obj):
        return bool(obj.audio_file or obj.audio_url)

    def get_thumbnail(self, obj):
        request = self.context.get('request')
        return obj.get_effective_thumbnail_url(request=request)


class WelcomeTutorialSerializer(serializers.ModelSerializer):
    """
    Serializer for Welcome Tutorial Video
    Supports both uploaded video file and external Video URL / YouTube link.
    """
    video_url = serializers.SerializerMethodField()
    video_embed_url = serializers.SerializerMethodField()
    is_youtube = serializers.SerializerMethodField()
    youtube_id = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = WelcomeTutorial
        fields = [
            'id',
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


class CheckInOverviewVideoSerializer(serializers.ModelSerializer):
    """
    Serializer for Check-in Overview Video
    Supports both uploaded video file and external Video URL / YouTube link.
    """
    video_url = serializers.SerializerMethodField()
    video_embed_url = serializers.SerializerMethodField()
    is_youtube = serializers.SerializerMethodField()
    youtube_id = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = CheckInOverviewVideo
        fields = [
            'id',
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


class CareTeamSupportVideoSerializer(serializers.ModelSerializer):
    """
    Serializer for Care Team Support Video
    Supports both uploaded video file and external Video URL / YouTube link.
    """
    video_url = serializers.SerializerMethodField()
    video_embed_url = serializers.SerializerMethodField()
    is_youtube = serializers.SerializerMethodField()
    youtube_id = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = CareTeamSupportVideo
        fields = [
            'id',
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


class ProgressOverviewVideoSerializer(serializers.ModelSerializer):
    """
    Serializer for Progress Overview Video
    Supports both uploaded video file and external Video URL / YouTube link.
    """
    video_url = serializers.SerializerMethodField()
    video_embed_url = serializers.SerializerMethodField()
    is_youtube = serializers.SerializerMethodField()
    youtube_id = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = ProgressOverviewVideo
        fields = [
            'id',
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


class UserLessonProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for user lesson progress status summary
    """
    current_day = serializers.SerializerMethodField()

    class Meta:
        model = UserLessonProgress
        fields = [
            'start_date',
            'current_day',
            'created_at',
            'updated_at',
        ]

    def get_current_day(self, obj):
        return obj.get_current_day()
