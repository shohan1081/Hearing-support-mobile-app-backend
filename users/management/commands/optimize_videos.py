"""
Re-encode existing uploaded videos for smooth mobile streaming.

New uploads are optimized automatically in the background; run this once for
videos uploaded before that, or to retry a failed/interrupted optimization.

    python manage.py optimize_videos --dry-run
    python manage.py optimize_videos
    python manage.py optimize_videos --model learn.welcometutorial
"""

from django.core.management.base import BaseCommand, CommandError

from users.video_processing import (
    VIDEO_FIELD,
    ffmpeg_available,
    needs_optimization,
    optimize_video,
    video_models,
)


class Command(BaseCommand):
    help = "Re-encode uploaded videos (720p H.264, faststart) for smooth mobile streaming."

    def add_arguments(self, parser):
        parser.add_argument('--model', help="Only this model, e.g. learn.welcometutorial")
        parser.add_argument('--dry-run', action='store_true', help="List videos that would be optimized")

    def handle(self, *args, **options):
        if not options['dry_run'] and not ffmpeg_available():
            raise CommandError("ffmpeg/ffprobe are not installed in this environment.")

        models = video_models()
        if options['model']:
            models = [m for m in models if m._meta.label_lower == options['model'].lower()]
            if not models:
                raise CommandError(f"No model with a '{VIDEO_FIELD}' field named {options['model']}")

        for model in models:
            rows = model.objects.exclude(**{VIDEO_FIELD: ''}).exclude(**{f'{VIDEO_FIELD}__isnull': True})
            for pk, name in rows.values_list('pk', VIDEO_FIELD):
                if not needs_optimization(name):
                    continue
                label = f"{model._meta.label} #{pk}: {name}"
                if options['dry_run']:
                    self.stdout.write(f"Would optimize {label}")
                    continue
                self.stdout.write(f"Optimizing {label} ...")
                try:
                    new_name = optimize_video(model, pk, name)
                except Exception as exc:
                    self.stderr.write(self.style.ERROR(f"  failed: {exc}"))
                    continue
                if new_name:
                    self.stdout.write(self.style.SUCCESS(f"  -> {new_name}"))
                else:
                    self.stdout.write("  skipped")
