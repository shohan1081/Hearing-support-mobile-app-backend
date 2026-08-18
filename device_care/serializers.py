from rest_framework import serializers
from .models import HearingAidBrand, HearingAidModel, DeviceCareSection, DeviceCareVideo


class DeviceCareVideoSerializer(serializers.ModelSerializer):
    """
    Serializer for tutorial videos inside care sections (e.g. cleaning tutorials)
    """
    video_url = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()

    class Meta:
        model = DeviceCareVideo
        fields = [
            'id',
            'order',
            'title',
            'description',
            'video_url',
            'has_video',
            'thumbnail',
            'duration_seconds',
            'created_at',
        ]

    def get_video_url(self, obj):
        request = self.context.get('request')
        return obj.get_video_stream_url(request=request)

    def get_has_video(self, obj):
        return bool(obj.video_file)


class DeviceCareSectionSerializer(serializers.ModelSerializer):
    """
    Serializer for care sections (Cleaning Guide, Care Tips, Troubleshooting, User Manual)
    """
    section_type_display = serializers.CharField(source='get_section_type_display', read_only=True)
    videos = serializers.SerializerMethodField()

    class Meta:
        model = DeviceCareSection
        fields = [
            'id',
            'section_type',
            'section_type_display',
            'order',
            'title',
            'subtitle',
            'content_text',
            'manual_url',
            'videos',
            'created_at',
            'updated_at',
        ]

    def get_videos(self, obj):
        active_videos = obj.videos.filter(is_active=True).order_by('order', 'created_at')
        return DeviceCareVideoSerializer(active_videos, many=True, context=self.context).data


class HearingAidModelListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing hearing aid models under a brand
    """
    image_url = serializers.SerializerMethodField()
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = HearingAidModel
        fields = [
            'id',
            'brand_name',
            'name',
            'slug',
            'image_url',
            'user_manual_url',
            'order',
            'created_at',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        return obj.get_image_url(request=request)


class HearingAidModelDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed hearing aid model info including all 4 care sections (cleaning, care tips, troubleshooting, manual)
    """
    image_url = serializers.SerializerMethodField()
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    sections = serializers.SerializerMethodField()

    class Meta:
        model = HearingAidModel
        fields = [
            'id',
            'brand_name',
            'name',
            'slug',
            'image_url',
            'description',
            'user_manual_url',
            'order',
            'sections',
            'created_at',
            'updated_at',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        return obj.get_image_url(request=request)

    def get_sections(self, obj):
        active_sections = obj.sections.filter(is_active=True).order_by('order', 'created_at')
        return DeviceCareSectionSerializer(active_sections, many=True, context=self.context).data


class HearingAidBrandListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing hearing aid brands (name, logo/image, models_count)
    """
    image_url = serializers.SerializerMethodField()
    models_count = serializers.SerializerMethodField()

    class Meta:
        model = HearingAidBrand
        fields = [
            'id',
            'name',
            'slug',
            'image_url',
            'description',
            'models_count',
            'order',
            'created_at',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        return obj.get_image_url(request=request)

    def get_models_count(self, obj):
        return obj.models.filter(is_active=True).count()


class HearingAidBrandDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed brand view including list of its hearing aid models
    """
    image_url = serializers.SerializerMethodField()
    models = serializers.SerializerMethodField()

    class Meta:
        model = HearingAidBrand
        fields = [
            'id',
            'name',
            'slug',
            'image_url',
            'description',
            'order',
            'models',
            'created_at',
            'updated_at',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        return obj.get_image_url(request=request)

    def get_models(self, obj):
        active_models = obj.models.filter(is_active=True).order_by('order', 'name')
        return HearingAidModelListSerializer(active_models, many=True, context=self.context).data
