"""
Direct browser-to-S3 video uploads for the Django Admin.

Why: a normal admin upload travels browser -> Nginx -> Gunicorn -> EC2 disk -> S3,
one single-stream hop after another. For a 180MB video that is minutes of waiting.
Here the browser uploads the file straight to S3 using parallel multipart PUTs
(presigned URLs), and the admin form only submits the resulting S3 key.

If the browser upload fails for any reason (e.g. bucket CORS not configured),
the file input is left untouched and the normal upload path still works.
"""

import json
import logging
import math
import os
import secrets

from django import forms
from django.apps import apps
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core import signing
from django.core.files.storage import default_storage
from django.db import models
from django.http import JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from .video_utils import ALLOWED_VIDEO_EXTENSIONS

try:
    from unfold.widgets import UnfoldAdminFileFieldWidget as BaseFileWidget
except ImportError:  # pragma: no cover
    from django.contrib.admin.widgets import AdminFileWidget as BaseFileWidget

logger = logging.getLogger(__name__)

SIGNING_SALT = 'users.direct_upload'
MIN_PART_SIZE = 10 * 1024 * 1024        # 10MB parts (S3 minimum is 5MB)
MAX_PARTS = 10000                        # S3 hard limit
PRESIGN_EXPIRES = 6 * 60 * 60            # 6h, enough for slow connections
TOKEN_MAX_AGE = 24 * 60 * 60
MAX_BASENAME_LENGTH = 40                 # keeps S3 names inside FileField max_length=100


def direct_upload_enabled():
    return bool(getattr(settings, 'USE_S3', False) and getattr(settings, 'VIDEO_DIRECT_UPLOAD', True))


def _s3_client():
    import boto3
    from botocore.config import Config

    return boto3.client(
        's3',
        region_name=getattr(settings, 'AWS_S3_REGION_NAME', None) or None,
        aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None) or None,
        aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None) or None,
        config=Config(
            signature_version='s3v4',
            s3={
                'addressing_style': 'virtual',
                'use_accelerate_endpoint': getattr(settings, 'VIDEO_UPLOAD_ACCELERATE', False),
            },
        ),
    )


def _field_label(model, field_name):
    return f"{model._meta.app_label}.{model._meta.model_name}.{field_name}"


def _resolve_field(label):
    """Resolve 'app.model.field' to a model FileField, only for video fields."""
    try:
        app_label, model_name, field_name = label.split('.')
        field = apps.get_model(app_label, model_name)._meta.get_field(field_name)
    except (ValueError, LookupError):
        return None
    if field_name != 'video_file' or not isinstance(field, models.FileField):
        return None
    return field


def _build_name(field, filename):
    """Storage name like 'learn/welcome_videos/my_video_3f9a1c2e.mp4'."""
    base, ext = os.path.splitext(os.path.basename(filename))
    base = default_storage.get_valid_name(base)[:MAX_BASENAME_LENGTH] or 'video'
    name = field.generate_filename(None, f"{base}_{secrets.token_hex(4)}{ext.lower()}")
    return name.replace(os.sep, '/')


def _s3_key(name):
    location = (getattr(settings, 'AWS_LOCATION', '') or '').strip('/')
    return f"{location}/{name}" if location else name


def _object_exists(name):
    # Not default_storage.exists(): django-storages 1.14.4 always returns False there
    # when AWS_S3_FILE_OVERWRITE is True (the default), without asking S3.
    from botocore.exceptions import ClientError

    try:
        _s3_client().head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=_s3_key(name))
        return True
    except ClientError as err:
        if err.response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 404:
            return False
        raise


def _json_body(request):
    try:
        return json.loads(request.body or b'{}')
    except ValueError:
        return {}


# ------------------------------------------------------------------------------
# Admin-only JSON endpoints used by static/users/js/direct_video_upload.js
# ------------------------------------------------------------------------------

@staff_member_required
@require_POST
def initiate_upload(request):
    data = _json_body(request)
    field = _resolve_field(data.get('field', ''))
    filename = str(data.get('filename', ''))
    size = int(data.get('size') or 0)
    content_type = str(data.get('content_type') or 'video/mp4')

    if field is None:
        return JsonResponse({'error': 'Unknown upload field.'}, status=400)
    if not filename.lower().endswith(ALLOWED_VIDEO_EXTENSIONS):
        return JsonResponse({'error': 'Unsupported video format.'}, status=400)
    max_bytes = getattr(settings, 'MAX_VIDEO_UPLOAD_SIZE_MB', 500) * 1024 * 1024
    if size <= 0 or size > max_bytes:
        return JsonResponse({'error': f'Video must be smaller than {max_bytes // (1024 * 1024)} MB.'}, status=400)
    if not content_type.startswith('video/'):
        content_type = 'video/mp4'

    name = _build_name(field, filename)
    key = _s3_key(name)
    part_size = max(MIN_PART_SIZE, math.ceil(size / MAX_PARTS))
    part_count = math.ceil(size / part_size)

    client = _s3_client()
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    extra = dict(getattr(settings, 'AWS_S3_OBJECT_PARAMETERS', {}) or {})
    extra['ContentType'] = content_type
    upload_id = client.create_multipart_upload(Bucket=bucket, Key=key, **extra)['UploadId']
    urls = [
        client.generate_presigned_url(
            'upload_part',
            Params={'Bucket': bucket, 'Key': key, 'UploadId': upload_id, 'PartNumber': n},
            ExpiresIn=PRESIGN_EXPIRES,
        )
        for n in range(1, part_count + 1)
    ]
    token = signing.dumps({'name': name, 'upload_id': upload_id}, salt=SIGNING_SALT)
    return JsonResponse({'token': token, 'part_size': part_size, 'urls': urls})


@staff_member_required
@require_POST
def complete_upload(request):
    data = _json_body(request)
    try:
        info = signing.loads(data.get('token', ''), salt=SIGNING_SALT, max_age=TOKEN_MAX_AGE)
    except signing.BadSignature:
        return JsonResponse({'error': 'Invalid upload token.'}, status=400)

    try:
        parts = sorted(
            ({'PartNumber': int(p['PartNumber']), 'ETag': str(p['ETag'])} for p in data.get('parts', [])),
            key=lambda p: p['PartNumber'],
        )
    except (KeyError, TypeError, ValueError):
        return JsonResponse({'error': 'Invalid parts list.'}, status=400)

    _s3_client().complete_multipart_upload(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=_s3_key(info['name']),
        UploadId=info['upload_id'],
        MultipartUpload={'Parts': parts},
    )
    # The form value is a signed storage name, so the form can't be pointed at arbitrary S3 keys.
    value = signing.dumps({'name': info['name']}, salt=SIGNING_SALT)
    return JsonResponse({'value': value, 'name': info['name']})


@staff_member_required
@require_POST
def abort_upload(request):
    data = _json_body(request)
    try:
        info = signing.loads(data.get('token', ''), salt=SIGNING_SALT, max_age=TOKEN_MAX_AGE)
        _s3_client().abort_multipart_upload(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=_s3_key(info['name']),
            UploadId=info['upload_id'],
        )
    except Exception as exc:  # best effort cleanup
        logger.warning("Failed to abort multipart upload: %s", exc)
    return JsonResponse({'ok': True})


urlpatterns = [
    path('initiate/', initiate_upload, name='video_direct_upload_initiate'),
    path('complete/', complete_upload, name='video_direct_upload_complete'),
    path('abort/', abort_upload, name='video_direct_upload_abort'),
]


# ------------------------------------------------------------------------------
# Admin form widget / field
# ------------------------------------------------------------------------------

class DirectS3VideoWidget(BaseFileWidget):
    token_suffix = '__direct'

    def __init__(self, field_label, attrs=None):
        self.field_label = field_label
        super().__init__(attrs)

    @property
    def media(self):
        return super().media + forms.Media(js=['users/js/direct_video_upload.js'])

    def render(self, name, value, attrs=None, renderer=None):
        attrs = {
            **(attrs or {}),
            'data-direct-upload': self.field_label,
            'data-initiate-url': reverse('video_direct_upload_initiate'),
            'data-complete-url': reverse('video_direct_upload_complete'),
            'data-abort-url': reverse('video_direct_upload_abort'),
        }
        file_input = super().render(name, value, attrs, renderer)
        return format_html(
            '<div data-direct-upload-wrapper>{}'
            '<input type="hidden" name="{}" value="" data-direct-upload-token>'
            '<div data-direct-upload-status style="margin-top:6px;font-size:12px;"></div>'
            '</div>',
            mark_safe(file_input),
            name + self.token_suffix,
        )

    def value_from_datadict(self, data, files, name):
        token = data.get(name + self.token_suffix)
        if token and not files.get(name):
            return token
        return super().value_from_datadict(data, files, name)

    def value_omitted_from_data(self, data, files, name):
        return (
            super().value_omitted_from_data(data, files, name)
            and name + self.token_suffix not in data
        )


class DirectS3VideoFormField(forms.FileField):
    """Accepts either a normal uploaded file or a signed name of a file already in S3."""

    def to_python(self, data):
        if isinstance(data, str):
            try:
                name = signing.loads(data, salt=SIGNING_SALT, max_age=TOKEN_MAX_AGE)['name']
            except (signing.BadSignature, KeyError, TypeError):
                raise forms.ValidationError(_("Upload expired or invalid. Please select the video again."))
            if not _object_exists(name):
                raise forms.ValidationError(_("Uploaded video was not found in storage. Please upload again."))
            return name
        return super().to_python(data)


class DirectVideoUploadAdminMixin:
    """Mix into a ModelAdmin / InlineModelAdmin to enable direct S3 upload for `video_file`."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if direct_upload_enabled() and db_field.name == 'video_file' and isinstance(db_field, models.FileField):
            kwargs['form_class'] = DirectS3VideoFormField
            kwargs['widget'] = DirectS3VideoWidget(_field_label(db_field.model, db_field.name))
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)
