from .models import DailyLesson, UserLessonProgress
from django.utils import timezone


def get_or_create_user_lesson_progress(user):
    """
    Get or create UserLessonProgress record for a user
    Defaults start_date to user's date_joined or today
    """
    progress, created = UserLessonProgress.objects.get_or_create(
        user=user,
        defaults={
            'start_date': user.date_joined.date() if hasattr(user, 'date_joined') and user.date_joined else timezone.now().date(),
            'completed_days': []
        }
    )
    return progress


def seed_default_daily_lessons():
    """
    Populate sample default daily lessons if none exist
    """
    DEFAULT_LESSONS = [
        {
            "day_number": 1,
            "title": "Day 1: Welcome to Your Hearing Journey",
            "subtitle": "Understanding your brain's adaptation to new sounds",
            "description": (
                "Welcome to Day 1 of your daily learning program! Today's lesson covers how your brain "
                "begins to process sound after starting your hearing improvement plan. Listen to the audio "
                "guide and watch the video to understand acoustic awareness."
            ),
            "key_takeaways": [
                "Your brain needs time to re-learn environmental sounds.",
                "Consistency in wearing your hearing aids is key.",
                "Start with quiet environments on Day 1."
            ],
            "video_file": "https://www.w3schools.com/html/mov_bbb.mp4",
            "audio_file": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
            "duration_seconds": 180,
        },
        {
            "day_number": 2,
            "title": "Day 2: Navigating Background Noise",
            "subtitle": "How to handle everyday ambient sounds without stress",
            "description": (
                "On Day 2, we explore background noise. Learn practical listening techniques to filter out "
                "unwanted ambient sounds like air conditioners, traffic, and dishes."
            ),
            "key_takeaways": [
                "Background noise is natural and expected.",
                "Focus on the speaker's face and lip movements.",
                "Take short listening breaks if you feel fatigued."
            ],
            "video_file": "https://www.w3schools.com/html/mov_bbb.mp4",
            "audio_file": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
            "duration_seconds": 210,
        },
        {
            "day_number": 3,
            "title": "Day 3: Speech Clarity in Quiet Settings",
            "subtitle": "Improving one-on-one conversation understanding",
            "description": (
                "Today we focus on one-on-one conversations. Listen to the audio practice track to train "
                "your auditory cortex on subtle speech consonants."
            ),
            "key_takeaways": [
                "High-frequency sounds like 's', 'f', and 'th' become clearer.",
                "Maintain direct line-of-sight during conversations.",
                "Ask speakers to slow down slightly rather than speak louder."
            ],
            "video_file": "https://www.w3schools.com/html/mov_bbb.mp4",
            "audio_file": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
            "duration_seconds": 195,
        },
        {
            "day_number": 4,
            "title": "Day 4: Listening to TV & Media",
            "subtitle": "Tips for clear TV, music, and phone audio",
            "description": (
                "Learn how to optimize media audio. Today's video and audio lesson demonstrates audio streaming, "
                "closed captioning strategies, and TV volume leveling."
            ),
            "key_takeaways": [
                "Use captions to help bridge speech understanding.",
                "Position yourself directly facing the television speakers.",
                "Explore direct bluetooth streaming if available."
            ],
            "video_file": "https://www.w3schools.com/html/mov_bbb.mp4",
            "audio_file": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
            "duration_seconds": 240,
        },
        {
            "day_number": 5,
            "title": "Day 5: Social Gatherings & Group Hearing",
            "subtitle": "Confidence in multi-person conversations",
            "description": (
                "Group conversations can be challenging. Day 5 teaches strategic seating and listening habits "
                "in restaurants and family gatherings."
            ),
            "key_takeaways": [
                "Sit with your back to the wall to reduce rear noise.",
                "Choose well-lit tables in restaurants.",
                "Focus on key conversation anchors."
            ],
            "video_file": "https://www.w3schools.com/html/mov_bbb.mp4",
            "audio_file": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
            "duration_seconds": 225,
        },
    ]

    for data in DEFAULT_LESSONS:
        DailyLesson.objects.get_or_create(
            day_number=data['day_number'],
            defaults={
                'title': data['title'],
                'subtitle': data['subtitle'],
                'description': data['description'],
                'key_takeaways': data['key_takeaways'],
                'video_file': data['video_file'],
                'audio_file': data['audio_file'],
                'duration_seconds': data['duration_seconds'],
                'is_active': True
            }
        )
