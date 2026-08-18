from django.db import models
from django.utils.translation import gettext_lazy as _


class HearingAidBrand(models.Model):
    """
    Hearing aid manufacturer brand (e.g. Phonak, Oticon, ReSound, Widex, Starkey)
    """
    name = models.CharField(
        _('brand name'),
        max_length=255,
        help_text=_("Brand name (e.g. Phonak, Oticon)")
    )
    slug = models.SlugField(
        _('slug'),
        max_length=100,
        unique=True,
        help_text=_("Unique identifier slug e.g. 'phonak', 'oticon'")
    )
    image = models.ImageField(
        _('brand logo / image'),
        upload_to='device_care/brands/',
        null=True,
        blank=True,
        help_text=_("Brand logo or cover image")
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Short description of the brand")
    )
    order = models.PositiveIntegerField(
        _('display order'),
        default=0,
        help_text=_("Ordering index (0, 1, 2...)")
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Whether this brand is active and visible to users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('hearing aid brand')
        verbose_name_plural = _('hearing aid brands')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_image_url(self, request=None):
        """Return absolute image URL"""
        if self.image:
            try:
                url = self.image.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return str(self.image)
        return ""


class HearingAidModel(models.Model):
    """
    Specific hearing aid device model belonging to a brand (e.g. Phonak Audéo Lumity)
    """
    brand = models.ForeignKey(
        HearingAidBrand,
        on_delete=models.CASCADE,
        related_name='models',
        verbose_name=_('brand'),
        help_text=_("Parent hearing aid brand")
    )
    name = models.CharField(
        _('model name'),
        max_length=255,
        help_text=_("Model name (e.g. Audéo Lumity, More 1)")
    )
    slug = models.SlugField(
        _('slug'),
        max_length=100,
        unique=True,
        help_text=_("Unique identifier slug e.g. 'audeo-lumity'")
    )
    image = models.ImageField(
        _('model picture'),
        upload_to='device_care/models/',
        null=True,
        blank=True,
        help_text=_("Picture of the hearing aid device model")
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Description of the device model features")
    )
    user_manual_url = models.URLField(
        _('user manual live URL'),
        blank=True,
        max_length=1000,
        help_text=_("Live web/PDF link to online user manual for this model")
    )
    order = models.PositiveIntegerField(
        _('display order'),
        default=0,
        help_text=_("Ordering index (0, 1, 2...)")
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Whether this model is active and visible to users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('hearing aid model')
        verbose_name_plural = _('hearing aid models')
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.brand.name} - {self.name}"

    def get_image_url(self, request=None):
        """Return absolute image URL"""
        if self.image:
            try:
                url = self.image.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return str(self.image)
        return ""


class DeviceCareSection(models.Model):
    """
    Care section for a hearing aid model (Cleaning Guide, Care Tips, Troubleshooting, User Manual)
    """
    SECTION_CLEANING_GUIDE = 'cleaning_guide'
    SECTION_CARE_TIPS = 'care_tips'
    SECTION_TROUBLESHOOTING = 'troubleshooting'
    SECTION_USER_MANUAL = 'user_manual'

    SECTION_CHOICES = (
        (SECTION_CLEANING_GUIDE, _('Cleaning Guide')),
        (SECTION_CARE_TIPS, _('Care Tips')),
        (SECTION_TROUBLESHOOTING, _('Troubleshooting')),
        (SECTION_USER_MANUAL, _('User Manual')),
    )

    model = models.ForeignKey(
        HearingAidModel,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name=_('device model'),
        help_text=_("Parent hearing aid model")
    )
    section_type = models.CharField(
        _('section type'),
        max_length=50,
        choices=SECTION_CHOICES,
        help_text=_("Select section type: Cleaning Guide, Care Tips, Troubleshooting, or User Manual")
    )
    title = models.CharField(
        _('section title'),
        max_length=255,
        help_text=_("Section title e.g. 'Daily Cleaning Tutorial'")
    )
    subtitle = models.CharField(
        _('subtitle'),
        max_length=500,
        blank=True,
        help_text=_("Short summary or subtitle")
    )
    content_text = models.TextField(
        _('text content / instructions'),
        blank=True,
        help_text=_("Detailed text instructions, step-by-step cleaning guides, or troubleshooting fixes")
    )
    manual_url = models.URLField(
        _('manual URL'),
        blank=True,
        max_length=1000,
        help_text=_("Live link to online user manual (used for User Manual section)")
    )
    order = models.PositiveIntegerField(
        _('display order'),
        default=0,
        help_text=_("Ordering index (0, 1, 2...)")
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Whether this section is active and visible to users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('device care section')
        verbose_name_plural = _('device care sections')
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.model.name} -> {self.get_section_type_display()}: {self.title}"


class DeviceCareVideo(models.Model):
    """
    Multiple tutorial videos attached to a Care Section (e.g. cleaning tutorial videos, troubleshooting videos)
    """
    section = models.ForeignKey(
        DeviceCareSection,
        on_delete=models.CASCADE,
        related_name='videos',
        verbose_name=_('care section'),
        help_text=_("Parent care section")
    )
    title = models.CharField(
        _('video title'),
        max_length=255,
        help_text=_("Video title e.g. 'How to replace wax guard filter'")
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Short video notes or step description")
    )
    video_file = models.FileField(
        _('video file'),
        upload_to='device_care/videos/',
        null=True,
        blank=True,
        help_text=_("Upload video file (MP4, MOV, etc.) or external link")
    )
    thumbnail = models.ImageField(
        _('thumbnail'),
        upload_to='device_care/video_thumbnails/',
        null=True,
        blank=True,
        help_text=_("Cover thumbnail image for the video")
    )
    duration_seconds = models.PositiveIntegerField(
        _('duration in seconds'),
        default=0,
        help_text=_("Duration of the video in seconds")
    )
    order = models.PositiveIntegerField(
        _('display order'),
        default=0,
        help_text=_("Ordering index (0, 1, 2...)")
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_("Whether this video is active and visible to users")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('device care video')
        verbose_name_plural = _('device care videos')
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title

    def get_video_stream_url(self, request=None):
        """Return absolute video stream URL"""
        if self.video_file:
            try:
                url = self.video_file.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return str(self.video_file)
        return ""
