from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import EverydayListeningTip


@admin.register(EverydayListeningTip)
class EverydayListeningTipAdmin(ModelAdmin):
    list_display = ('title', 'slug', 'order', 'is_active', 'updated_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'slug', 'subtitle', 'description')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'subtitle', 'order', 'is_active')
        }),
        ('Tip Description & Guidance', {
            'fields': ('description',)
        }),
        ('Upload Audio & Thumbnail', {
            'fields': ('audio_file', 'thumbnail')
        }),
    )
