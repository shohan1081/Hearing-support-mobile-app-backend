"""
Video & Media Utility Helpers
Provides centralized YouTube URL extraction, embed formatting, thumbnail resolution,
and file size validation for videos and audio across all apps.
"""

import re
from urllib.parse import urlparse, parse_qs
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Maximum upload size for video files in megabytes (default: 500MB)
DEFAULT_MAX_VIDEO_SIZE_MB = getattr(settings, 'MAX_VIDEO_UPLOAD_SIZE_MB', 500)
DEFAULT_MAX_AUDIO_SIZE_MB = 100

ALLOWED_VIDEO_EXTENSIONS = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.3gp', '.flv', '.wmv')
ALLOWED_AUDIO_EXTENSIONS = ('.mp3', '.wav', '.aac', '.m4a', '.ogg', '.flac', '.wma')


def validate_video_file_size(file):
    """
    Validate uploaded video file size against server upload limit (500MB)
    and check for valid video extension.
    """
    if not file:
        return

    max_mb = getattr(settings, 'MAX_VIDEO_UPLOAD_SIZE_MB', DEFAULT_MAX_VIDEO_SIZE_MB)
    max_bytes = max_mb * 1024 * 1024

    file_name = getattr(file, 'name', '').lower()
    if file_name and not any(file_name.endswith(ext) for ext in ALLOWED_VIDEO_EXTENSIONS):
        valid_exts = ", ".join(ALLOWED_VIDEO_EXTENSIONS)
        raise ValidationError(
            _(f"Invalid video file format. Supported video formats are: {valid_exts}"),
            code='invalid_video_format'
        )

    file_size = getattr(file, 'size', 0)
    if file_size > max_bytes:
        size_mb = file_size / (1024 * 1024)
        raise ValidationError(
            _(
                f"The uploaded video file size ({size_mb:.1f} MB) exceeds the maximum server limit "
                f"of {max_mb} MB. Please compress your video or use the 'Video URL' field to link "
                f"an Unlisted YouTube video."
            ),
            code='video_file_too_large'
        )


def validate_audio_file_size(file):
    """
    Validate uploaded audio file size against server upload limit (100MB).
    """
    if not file:
        return

    max_mb = DEFAULT_MAX_AUDIO_SIZE_MB
    max_bytes = max_mb * 1024 * 1024

    file_name = getattr(file, 'name', '').lower()
    if file_name and not any(file_name.endswith(ext) for ext in ALLOWED_AUDIO_EXTENSIONS):
        valid_exts = ", ".join(ALLOWED_AUDIO_EXTENSIONS)
        raise ValidationError(
            _(f"Invalid audio file format. Supported audio formats are: {valid_exts}"),
            code='invalid_audio_format'
        )

    file_size = getattr(file, 'size', 0)
    if file_size > max_bytes:
        size_mb = file_size / (1024 * 1024)
        raise ValidationError(
            _(
                f"The uploaded audio file size ({size_mb:.1f} MB) exceeds the maximum limit "
                f"of {max_mb} MB. Please compress your audio file or provide a direct stream link."
            ),
            code='audio_file_too_large'
        )


def extract_youtube_id(url):
    """
    Extract YouTube Video ID (11 characters) from all valid YouTube URL formats.
    
    Supports:
    - https://www.youtube.com/watch?v=dQw4w9WgXcQ
    - https://youtu.be/dQw4w9WgXcQ
    - https://www.youtube.com/embed/dQw4w9WgXcQ
    - https://www.youtube.com/v/dQw4w9WgXcQ
    - https://youtube.com/shorts/dQw4w9WgXcQ
    - https://m.youtube.com/watch?v=dQw4w9WgXcQ
    - With timestamps or extra params (?v=...&t=10s)
    
    Returns:
        str: 11-char video ID or None
    """
    if not url:
        return None

    clean_url = str(url).strip()
    if not clean_url:
        return None

    # If user accidentally pasted just the 11-char ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', clean_url):
        return clean_url

    patterns = [
        # youtu.be/<id>
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})',
        # youtube.com/watch?v=<id> or m.youtube.com/watch?v=<id>
        r'(?:https?:\/\/)?(?:www\.|m\.)?youtube\.com\/(?:watch\?.*?v=|embed\/|v\/|shorts\/)([a-zA-Z0-9_-]{11})',
        # youtube-nocookie.com/embed/<id>
        r'(?:https?:\/\/)?(?:www\.)?youtube-nocookie\.com\/embed\/([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, clean_url)
        if match:
            return match.group(1)

    # Fallback to urllib query parsing
    try:
        parsed = urlparse(clean_url)
        if 'youtube' in parsed.netloc:
            qs = parse_qs(parsed.query)
            if 'v' in qs and qs['v']:
                v_id = qs['v'][0]
                if re.match(r'^[a-zA-Z0-9_-]{11}$', v_id):
                    return v_id
    except Exception:
        pass

    return None


def is_youtube_url(url):
    """
    Check if given URL points to a YouTube video.
    """
    return bool(extract_youtube_id(url))


def get_youtube_embed_url(url_or_id):
    """
    Generate clean, responsive YouTube iframe embed player URL.
    
    Args:
        url_or_id: Full YouTube URL or extracted video ID
        
    Returns:
        str: https://www.youtube.com/embed/<ID>?autoplay=0&rel=0&modestbranding=1
    """
    video_id = extract_youtube_id(url_or_id)
    if video_id:
        return f"https://www.youtube.com/embed/{video_id}?autoplay=0&rel=0&modestbranding=1"
    return ""


def get_youtube_thumbnail_url(url_or_id, quality='hq'):
    """
    Get YouTube thumbnail image URL.
    
    Quality options:
    - 'hq': hqdefault.jpg (480x360)
    - 'mq': mqdefault.jpg (320x180)
    - 'maxres': maxresdefault.jpg (1280x720)
    """
    video_id = extract_youtube_id(url_or_id)
    if video_id:
        if quality == 'maxres':
            return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        elif quality == 'mq':
            return f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
        return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    return ""


def resolve_video_data(video_file=None, video_url=None, thumbnail=None, request=None):
    """
    Consolidated helper to resolve video stream URL, embed URL, YouTube status,
    and effective thumbnail for any model instance.
    """
    stream_url = ""
    embed_url = ""
    yt_id = None
    is_yt = False

    if video_file:
        try:
            url = video_file.url
            if request and not url.startswith('http'):
                stream_url = request.build_absolute_uri(url)
            else:
                stream_url = url
        except Exception:
            stream_url = str(video_file)
    elif video_url:
        clean_url = str(video_url).strip()
        yt_id = extract_youtube_id(clean_url)
        if yt_id:
            is_yt = True
            embed_url = get_youtube_embed_url(yt_id)
            stream_url = clean_url
        else:
            stream_url = clean_url
            embed_url = clean_url

    # Effective thumbnail
    thumbnail_url = ""
    if thumbnail:
        try:
            t_url = thumbnail.url
            if request and not t_url.startswith('http'):
                thumbnail_url = request.build_absolute_uri(t_url)
            else:
                thumbnail_url = t_url
        except Exception:
            thumbnail_url = str(thumbnail)
    elif is_yt and yt_id:
        # Fallback to YouTube's auto-generated thumbnail if user didn't upload a custom thumbnail
        thumbnail_url = get_youtube_thumbnail_url(yt_id, quality='hq')

    return {
        "stream_url": stream_url,
        "embed_url": embed_url,
        "is_youtube": is_yt,
        "youtube_id": yt_id,
        "has_video": bool(stream_url),
        "thumbnail_url": thumbnail_url,
    }


from django.utils.html import format_html


def get_video_status_badge(obj):
    """
    Generate color-coded badge for Django Admin changelist view.
    """
    if getattr(obj, 'video_file', None):
        return format_html('<span style="background: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 9999px; font-weight: 600; font-size: 11px;">📁 Video File</span>')
    elif getattr(obj, 'video_url', None):
        is_yt = getattr(obj, 'is_youtube_video', lambda: False)()
        if is_yt:
            return format_html('<span style="background: #fee2e2; color: #991b1b; padding: 2px 8px; border-radius: 9999px; font-weight: 600; font-size: 11px;">🔴 YouTube</span>')
        return format_html('<span style="background: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 9999px; font-weight: 600; font-size: 11px;">🔗 External URL</span>')
    return format_html('<span style="background: #f3f4f6; color: #6b7280; padding: 2px 8px; border-radius: 9999px; font-weight: 500; font-size: 11px;">❌ No Video</span>')


def render_video_preview_html(obj):
    """
    Render HTML video player or YouTube iframe preview in Django Admin change view.
    """
    if not obj or not getattr(obj, 'id', None):
        return format_html('<span style="color: #9ca3af;">Save entry first to view video preview.</span>')

    # Check if YouTube video
    is_yt = getattr(obj, 'is_youtube_video', lambda: False)()
    if is_yt:
        embed_url = getattr(obj, 'get_embed_url', lambda: '')()
        raw_url = getattr(obj, 'video_url', '') or ''
        return format_html(
            '<div style="margin-top: 8px;">'
            '<iframe width="360" height="202" src="{}" title="YouTube Video Player" frameborder="0" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen style="border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">'
            '</iframe>'
            '<p style="font-size: 12px; color: #6b7280; margin-top: 4px;">'
            'YouTube Source: <a href="{}" target="_blank" style="color: #2563eb; text-decoration: underline;">{}</a> '
            '(Ensure video is set to <strong>Unlisted</strong> on YouTube)'
            '</p>'
            '</div>',
            embed_url,
            raw_url,
            raw_url[:60] + '...' if len(raw_url) > 60 else raw_url
        )

    # Check if direct file or external video stream
    stream_url = getattr(obj, 'get_video_stream_url', lambda: '')()
    if stream_url:
        return format_html(
            '<div style="margin-top: 8px;">'
            '<video width="360" height="202" controls style="border-radius: 8px; background: #000; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">'
            '<source src="{}" type="video/mp4">'
            'Your browser does not support the video tag.'
            '</video>'
            '<p style="font-size: 12px; color: #6b7280; margin-top: 4px;">'
            'Stream Source: <a href="{}" target="_blank" style="color: #2563eb; text-decoration: underline;">{}</a>'
            '</p>'
            '</div>',
            stream_url,
            stream_url,
            stream_url[:60] + '...' if len(stream_url) > 60 else stream_url
        )

    return format_html('<span style="color: #9ca3af;">No video uploaded or linked yet.</span>')
