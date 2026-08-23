from django.core.management.base import BaseCommand
from users.models import CheckInTutorial

SAMPLE_TUTORIALS = [
    {
        "title": "Sounds are too loud",
        "slug": "sounds-are-too-loud",
        "category": "Sound Adjustment",
        "order": 1,
        "description": "If everyday sounds like running water, dishes clattering, or footsteps feel sharp and painfully loud, your brain is adapting to newly amplified frequencies.",
        "video_url": "https://vjs.zencdn.net/v/oceans.mp4"
    },
    {
        "title": "I hear but don't understand",
        "slug": "i-hear-but-dont-understand",
        "category": "Speech Clarity",
        "order": 2,
        "description": "Hearing sound without clear word distinction is common during the first few weeks. Practice active listening in quiet environments first.",
        "video_url": "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"
    },
    {
        "title": "Background noise is distracting",
        "slug": "background-noise-is-distracting",
        "category": "Noisy Environments",
        "order": 3,
        "description": "Background noise can feel overwhelming initially. Use your hearing aid app to adjust directional microphones or reduce noise level.",
        "video_url": "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/friday.mp4"
    },
    {
        "title": "Restaurants are hard",
        "slug": "restaurants-are-hard",
        "category": "Social Settings",
        "order": 4,
        "description": "Restaurants have complex reverberation and clatter. Choose corner seating, sit with your back to the wall, and activate the speech in noise program.",
        "video_url": "https://cdn.plyr.io/static/demo/View_From_A_Blue_Moon_Trailer-720p.mp4"
    },
    {
        "title": "TV is unclear",
        "slug": "tv-is-unclear",
        "category": "Media & TV",
        "order": 5,
        "description": "TV speakers often produce flat audio. Consider using direct Bluetooth streaming or a TV streamer accessory for crystal clear dialogue.",
        "video_url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/720/Big_Buck_Bunny_720_10s_1MB.mp4"
    },
    {
        "title": "I feel overwhelmed",
        "slug": "i-feel-overwhelmed",
        "category": "Adjustment & Fatigue",
        "order": 6,
        "description": "Listening fatigue is normal. Take a 30-minute listening break in a quiet room, then put your hearing aids back in.",
        "video_url": "https://vjs.zencdn.net/v/oceans.mp4"
    },
    {
        "title": "Other",
        "slug": "other",
        "category": "General",
        "order": 7,
        "description": "If you are experiencing other hearing challenges or device issues, let our care team know and schedule a consultation.",
        "video_url": None
    }
]

class Command(BaseCommand):
    help = "Seed or update default Check-in Tutorials"

    def handle(self, *args, **kwargs):
        created_count = 0
        updated_count = 0
        for item in SAMPLE_TUTORIALS:
            tut, created = CheckInTutorial.objects.get_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "category": item["category"],
                    "order": item["order"],
                    "description": item["description"],
                    "video_url": item.get("video_url"),
                    "is_active": True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created tutorial: {tut.title} (slug: {tut.slug})"))
            else:
                if not tut.video_url or 'commondatastorage.googleapis.com' in str(tut.video_url):
                    tut.video_url = item.get("video_url")
                    tut.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated video URL for: {tut.title} (ID: {tut.id})"))
                else:
                    self.stdout.write(self.style.WARNING(f"Tutorial already exists: {tut.title} (ID: {tut.id}, slug: {tut.slug})"))

        self.stdout.write(self.style.SUCCESS(f"Seeding finished. Newly created: {created_count}, Updated URLs: {updated_count}"))
