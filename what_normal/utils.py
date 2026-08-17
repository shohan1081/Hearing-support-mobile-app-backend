from .models import WhatNormalVideo, WhatNormalAudio


def seed_default_what_normal_media():
    """
    Populate default sample videos and audios for What's Normal feature if none exist
    """
    if not WhatNormalVideo.objects.exists():
        DEFAULT_VIDEOS = [
            {
                "order": 1,
                "title": "Why Sounds Feel Too Loud At First",
                "subtitle": "Understanding auditory brain retraining",
                "description": (
                    "When you first begin your hearing adaptation plan, everyday sounds like chewing food, "
                    "paper rustling, or footsteps might feel unnaturally loud. This video explains why your "
                    "brain is adjusting and why this temporary phase is completely normal."
                ),
                "video_file": "https://www.w3schools.com/html/mov_bbb.mp4",
                "duration_seconds": 150,
            },
            {
                "order": 2,
                "title": "Hearing Your Own Voice Clearly",
                "subtitle": "Navigating the occlusion effect naturally",
                "description": (
                    "Hearing your own voice sound hollow or echoey is a standard part of early hearing aid "
                    "acclimation. Learn simple tips to speak comfortably as your vocal perception normalizes."
                ),
                "video_file": "https://www.w3schools.com/html/mov_bbb.mp4",
                "duration_seconds": 180,
            },
            {
                "order": 3,
                "title": "Managing Listening Fatigue",
                "subtitle": "Pacing your daily hearing practice safely",
                "description": (
                    "Processing new sounds requires extra energy from your brain. This video offers practical "
                    "guidance on taking listening breaks without interrupting your progress."
                ),
                "video_file": "https://www.w3schools.com/html/mov_bbb.mp4",
                "duration_seconds": 210,
            },
        ]
        for data in DEFAULT_VIDEOS:
            WhatNormalVideo.objects.create(
                order=data['order'],
                title=data['title'],
                subtitle=data['subtitle'],
                description=data['description'],
                video_file=data['video_file'],
                duration_seconds=data['duration_seconds'],
                is_active=True
            )

    if not WhatNormalAudio.objects.exists():
        DEFAULT_AUDIOS = [
            {
                "order": 1,
                "title": "Acoustic Acclimation Audio Guide",
                "subtitle": "Guided audio walkthrough for environmental sounds",
                "description": (
                    "Listen to this audio guide to train your brain to filter ambient background sounds like "
                    "refrigerator hums, clocks, and distant traffic."
                ),
                "audio_file": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                "duration_seconds": 240,
            },
            {
                "order": 2,
                "title": "Speech Consonants Listening Track",
                "subtitle": "Refining high-frequency speech sound distinction",
                "description": (
                    "Listen to this sound practice session to improve your clarity when hearing soft consonants "
                    "such as 'S', 'F', 'T', and 'SH' in quiet settings."
                ),
                "audio_file": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
                "duration_seconds": 300,
            },
        ]
        for data in DEFAULT_AUDIOS:
            WhatNormalAudio.objects.create(
                order=data['order'],
                title=data['title'],
                subtitle=data['subtitle'],
                description=data['description'],
                audio_file=data['audio_file'],
                duration_seconds=data['duration_seconds'],
                is_active=True
            )
