from rest_framework import serializers
from .models import EverydayListeningTip


class SkillStrategyAudioSerializer(serializers.ModelSerializer):
    """
    Serializer for Skills & Strategies audio sections across all categories
    """
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    audio_stream_url = serializers.SerializerMethodField()
    audio_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    has_audio = serializers.SerializerMethodField()
    duration_formatted = serializers.CharField(read_only=True)

    class Meta:
        model = EverydayListeningTip
        fields = [
            'id',
            'category',
            'category_display',
            'slug',
            'order',
            'title',
            'subtitle',
            'description',
            'audio_stream_url',
            'audio_url',
            'has_audio',
            'thumbnail_url',
            'duration_seconds',
            'duration_formatted',
            'is_active',
            'created_at',
            'updated_at',
        ]

    def get_audio_stream_url(self, obj):
        request = self.context.get('request')
        return obj.get_audio_stream_url(request=request)

    def get_audio_url(self, obj):
        request = self.context.get('request')
        return obj.get_audio_stream_url(request=request)

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        return obj.get_thumbnail_url(request=request)

    def get_has_audio(self, obj):
        return bool(obj.audio_file or obj.audio_url)


# Backward-compatibility alias
EverydayListeningTipListSerializer = SkillStrategyAudioSerializer
EverydayListeningTipDetailSerializer = SkillStrategyAudioSerializer