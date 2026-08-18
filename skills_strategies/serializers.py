from rest_framework import serializers
from .models import EverydayListeningTip


class EverydayListeningTipListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Everyday Listening Tips
    """
    audio_url = serializers.SerializerMethodField()
    has_audio = serializers.SerializerMethodField()

    class Meta:
        model = EverydayListeningTip
        fields = [
            'id',
            'slug',
            'order',
            'title',
            'subtitle',
            'audio_url',
            'has_audio',
            'thumbnail',
            'duration_seconds',
            'created_at',
        ]

    def get_audio_url(self, obj):
        request = self.context.get('request')
        return obj.get_audio_stream_url(request=request)

    def get_has_audio(self, obj):
        return bool(obj.audio_file)


class EverydayListeningTipDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Everyday Listening Tip & audio player
    """
    audio_url = serializers.SerializerMethodField()
    has_audio = serializers.SerializerMethodField()

    class Meta:
        model = EverydayListeningTip
        fields = [
            'id',
            'slug',
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
        return bool(obj.audio_file)
