from .models import EverydayListeningTip


def seed_default_everyday_listening_tips():
    """
    Populate the 5 default Everyday Listening Tips with audio files if none exist
    """
    DEFAULT_TIPS = [
        {
            "order": 1,
            "slug": "reduce-background-noise",
            "title": "Reduce Background Noise",
            "subtitle": "Minimize ambient acoustic distractions before starting conversations",
            "description": (
                "Background noise can make listening significantly harder. Before beginning a conversation, "
                "lower the volume on televisions, move away from loud appliances like dishwashers or fans, "
                "and choose quiet seating areas in restaurants."
            ),
            "audio_file": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
            "duration_seconds": 120,
        },
        {
            "order": 2,
            "slug": "face-the-speaker",
            "title": "Face the Speaker",
            "subtitle": "Position yourself directly facing whoever is speaking",
            "description": (
                "Direct line-of-sight visual contact improves sound reception and allows your brain to combine "
                "auditory cues with lip-reading and facial expressions. Always ensure you are in the same room "
                "and facing the person talking to you."
            ),
            "audio_file": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
            "duration_seconds": 135,
        },
        {
            "order": 3,
            "slug": "take-breaks",
            "title": "Take Breaks",
            "subtitle": "Give your auditory cortex short rest periods during noisy days",
            "description": (
                "Listening in complex soundscapes requires heightened mental effort. If you feel tired or overwhelmed, "
                "step into a quiet room for 5 to 10 minutes to let your auditory brain relax and recharge."
            ),
            "audio_file": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
            "duration_seconds": 150,
        },
        {
            "order": 4,
            "slug": "use-visual-cues",
            "title": "Use Visual Cues",
            "subtitle": "Leverage body language, gestures, and facial expressions",
            "description": (
                "Visual cues provide essential context to speech comprehension. Pay attention to hand gestures, "
                "body posture, and lip movements to help fill in missing speech sounds seamlessly."
            ),
            "audio_file": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
            "duration_seconds": 140,
        },
        {
            "order": 5,
            "slug": "ask-for-repetition",
            "title": "Ask for Repetition",
            "subtitle": "Politely ask speakers to rephrase or speak clearly",
            "description": (
                "If you miss a word or phrase, ask the speaker to rephrase the sentence rather than just repeating "
                "it louder. Rephrased wording often uses different speech frequencies that are easier to understand."
            ),
            "audio_file": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
            "duration_seconds": 160,
        },
    ]

    for data in DEFAULT_TIPS:
        EverydayListeningTip.objects.get_or_create(
            slug=data['slug'],
            defaults={
                'order': data['order'],
                'title': data['title'],
                'subtitle': data['subtitle'],
                'description': data['description'],
                'audio_file': data['audio_file'],
                'duration_seconds': data['duration_seconds'],
                'is_active': True
            }
        )
