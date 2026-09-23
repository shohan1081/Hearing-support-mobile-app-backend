"""
Add the S3 bucket CORS rule required for direct browser-to-S3 admin video uploads.

    python manage.py configure_s3_cors

Existing CORS rules on the bucket are kept; the admin-upload rule is added/replaced.
Requires the s3:GetBucketCORS and s3:PutBucketCORS permissions (or add the same rule
manually in the S3 console -> bucket -> Permissions -> CORS).
"""

from botocore.exceptions import ClientError
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from users.direct_upload import _s3_client

RULE_ID = 'admin-direct-video-upload'


class Command(BaseCommand):
    help = "Configure S3 bucket CORS for direct admin video uploads."

    def handle(self, *args, **options):
        if not getattr(settings, 'USE_S3', False):
            raise CommandError("USE_S3 is not enabled.")

        origins = sorted({o for o in settings.CSRF_TRUSTED_ORIGINS if o.startswith('https://')})
        if not origins:
            raise CommandError("No https:// origins in CSRF_TRUSTED_ORIGINS.")

        client = _s3_client()
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        try:
            rules = client.get_bucket_cors(Bucket=bucket)['CORSRules']
        except ClientError as exc:
            if exc.response['Error']['Code'] != 'NoSuchCORSConfiguration':
                raise
            rules = []

        rules = [r for r in rules if r.get('ID') != RULE_ID]
        rules.append({
            'ID': RULE_ID,
            'AllowedOrigins': origins,
            'AllowedMethods': ['PUT', 'GET', 'HEAD'],
            'AllowedHeaders': ['*'],
            'ExposeHeaders': ['ETag'],
            'MaxAgeSeconds': 3600,
        })
        client.put_bucket_cors(Bucket=bucket, CORSConfiguration={'CORSRules': rules})
        self.stdout.write(self.style.SUCCESS(f"CORS configured on {bucket} for: {', '.join(origins)}"))
