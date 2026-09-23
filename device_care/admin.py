from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from users.direct_upload import DirectVideoUploadAdminMixin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from users.video_utils import get_video_status_badge, render_video_preview_html
from .models import HearingAidBrand, HearingAidModel, DeviceCareSection, DeviceCareVideo


class DeviceCareVideoInline(DirectVideoUploadAdminMixin, TabularInline):
    model = DeviceCareVideo
    extra = 1
    fields = ('title', 'video_file', 'video_url', 'thumbnail', 'duration_seconds', 'order', 'is_active')


class DeviceCareSectionInline(StackedInline):
    model = DeviceCareSection
    extra = 1
    fields = ('section_type', 'title', 'subtitle', 'content_text', 'manual_url', 'order', 'is_active')


class HearingAidModelInline(TabularInline):
    model = HearingAidModel
    extra = 1
    fields = ('name', 'slug', 'image', 'user_manual_url', 'order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(HearingAidBrand)
class HearingAidBrandAdmin(ModelAdmin):
    list_display = ('title_display', 'slug', 'order', 'models_count', 'is_active', 'updated_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
    inlines = [HearingAidModelInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'order', 'is_active')
        }),
        ('Brand Details & Logo', {
            'fields': ('image', 'description')
        }),
    )

    def title_display(self, obj):
        return obj.name
    title_display.short_description = 'Brand Name'

    def models_count(self, obj):
        return obj.models.count()
    models_count.short_description = 'Models Count'


@admin.register(HearingAidModel)
class HearingAidModelAdmin(ModelAdmin):
    list_display = ('title_display', 'brand', 'slug', 'user_manual_url', 'order', 'is_active', 'updated_at')
    list_editable = ('order', 'is_active')
    list_filter = ('brand', 'is_active')
    search_fields = ('name', 'slug', 'description', 'brand__name')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('brand', 'order', 'name')
    inlines = [DeviceCareSectionInline]

    fieldsets = (
        (None, {
            'fields': ('brand', 'name', 'slug', 'order', 'is_active')
        }),
        ('Device Picture & Overview', {
            'fields': ('image', 'description')
        }),
        ('Live User Manual', {
            'fields': ('user_manual_url',)
        }),
    )

    def title_display(self, obj):
        return obj.name
    title_display.short_description = 'Model Name'


@admin.register(DeviceCareSection)
class DeviceCareSectionAdmin(ModelAdmin):
    list_display = ('title_display', 'model', 'section_type', 'videos_count', 'order', 'is_active', 'updated_at')
    list_editable = ('order', 'is_active')
    list_filter = ('section_type', 'model__brand', 'is_active')
    search_fields = ('title', 'subtitle', 'content_text', 'model__name')
    ordering = ('model', 'order')
    inlines = [DeviceCareVideoInline]

    fieldsets = (
        (None, {
            'fields': ('model', 'section_type', 'title', 'subtitle', 'order', 'is_active')
        }),
        ('Section Text Instructions & Content', {
            'fields': ('content_text', 'manual_url')
        }),
    )

    def title_display(self, obj):
        return obj.title
    title_display.short_description = 'Section Title'

    def videos_count(self, obj):
        return obj.videos.count()
    videos_count.short_description = 'Tutorial Videos Count'


@admin.register(DeviceCareVideo)
class DeviceCareVideoAdmin(DirectVideoUploadAdminMixin, ModelAdmin):
    list_display = ('title_display', 'section', 'video_status', 'order', 'is_active', 'updated_at')
    list_editable = ('order', 'is_active')
    list_filter = ('section__section_type', 'section__model', 'is_active')
    search_fields = ('title', 'description', 'section__title')
    ordering = ('section', 'order')
    readonly_fields = ('video_preview', 'created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('section', 'title', 'order', 'is_active')
        }),
        ('Video Description & Notes', {
            'fields': ('description',)
        }),
        ('Video Media (Upload File or Enter URL)', {
            'fields': (
                'video_file',
                'video_url',
                'thumbnail',
                'video_preview',
                'duration_seconds',
            ),
            'description': _(
                "Upload a video file directly (Max 500MB) OR enter a video URL / YouTube link. "
                "For YouTube videos, ensure they are set to <strong>Unlisted</strong> so patients can play them without signing in. "
                "You can upload a custom thumbnail for either option."
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def title_display(self, obj):
        return obj.title
    title_display.short_description = 'Video Title'

    def video_status(self, obj):
        return get_video_status_badge(obj)
    video_status.short_description = _("Video Source")

    def video_preview(self, obj):
        return render_video_preview_html(obj)
    video_preview.short_description = _("Video Preview")
