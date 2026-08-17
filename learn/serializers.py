from rest_framework import serializers
from .models import DailyLesson, UserLessonProgress


class DailyLessonSerializer(serializers.ModelSerializer):
    """
    Serializer for Today's Lesson (video and audio content)
    """
    video_url = serializers.SerializerMethodField()
    audio_url = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    has_audio = serializers.SerializerMethodField()

    class Meta:
        model = DailyLesson
        fields = [
            'id',
            'day_number',
            'title',
            'subtitle',
            'description',
            'video_url',
            'audio_url',
            'has_video',
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

    def get_audio_url(self, obj):
        request = self.context.get('request')
        return obj.get_audio_stream_url(request=request)

    def get_has_video(self, obj):
        return bool(obj.video_file)

    def get_has_audio(self, obj):
        return bool(obj.audio_file)


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
