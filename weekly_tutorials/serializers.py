from rest_framework import serializers
from .models import WeeklyTutorial, UserWeeklyProgress


class WeeklyTutorialListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing weekly tutorials with user progress status
    Supports both uploaded video file and external Video URL / YouTube link.
    """
    video_url = serializers.SerializerMethodField()
    video_embed_url = serializers.SerializerMethodField()
    is_youtube = serializers.SerializerMethodField()
    youtube_id = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    is_unlocked = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = WeeklyTutorial
        fields = [
            'id',
            'week_number',
            'title',
            'banner_text',
            'thumbnail',
            'video_url',
            'video_embed_url',
            'is_youtube',
            'youtube_id',
            'has_video',
            'duration_seconds',
            'is_unlocked',
            'is_current',
            'is_completed',
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

    def _get_progress(self):
        return self.context.get('user_progress')

    def get_is_unlocked(self, obj):
        progress = self._get_progress()
        if not progress:
            return obj.week_number == 1
        return progress.is_week_unlocked(obj.week_number)

    def get_is_current(self, obj):
        progress = self._get_progress()
        if not progress:
            return obj.week_number == 1
        return progress.get_current_week() == obj.week_number

    def get_is_completed(self, obj):
        progress = self._get_progress()
        if not progress:
            return False
        return progress.is_week_completed(obj.week_number)


class WeeklyTutorialDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed view of a weekly tutorial
    Supports both uploaded video file and external Video URL / YouTube link.
    """
    video_url = serializers.SerializerMethodField()
    video_embed_url = serializers.SerializerMethodField()
    is_youtube = serializers.SerializerMethodField()
    youtube_id = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    is_unlocked = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = WeeklyTutorial
        fields = [
            'id',
            'week_number',
            'title',
            'banner_text',
            'description',
            'video_url',
            'video_embed_url',
            'is_youtube',
            'youtube_id',
            'has_video',
            'thumbnail',
            'duration_seconds',
            'what_you_will_learn',
            'is_unlocked',
            'is_current',
            'is_completed',
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

    def _get_progress(self):
        return self.context.get('user_progress')

    def get_is_unlocked(self, obj):
        progress = self._get_progress()
        if not progress:
            return obj.week_number == 1
        return progress.is_week_unlocked(obj.week_number)

    def get_is_current(self, obj):
        progress = self._get_progress()
        if not progress:
            return obj.week_number == 1
        return progress.get_current_week() == obj.week_number

    def get_is_completed(self, obj):
        progress = self._get_progress()
        if not progress:
            return False
        return progress.is_week_completed(obj.week_number)


class UserWeeklyProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for user weekly progress status summary
    """
    current_week = serializers.SerializerMethodField()

    class Meta:
        model = UserWeeklyProgress
        fields = [
            'journey_start_date',
            'current_week',
            'completed_weeks',
            'created_at',
            'updated_at',
        ]

    def get_current_week(self, obj):
        return obj.get_current_week()
