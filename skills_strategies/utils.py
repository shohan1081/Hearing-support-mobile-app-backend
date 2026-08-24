from .models import EverydayListeningTip


def seed_default_everyday_listening_tips():
    """
    Populate the 5 official Skills & Strategies audio sections:
    1. Start the conversation
    2. Manage group conversations
    3. Improve understanding
    4. Handle misunderstandings
    5. Build stronger connections
    """
    DEFAULT_SECTIONS = [
        {
            "order": 1,
            "slug": "start-the-conversation",
            "title": "Start the conversation",
            "subtitle": "Confidence, positioning, and mindset strategies to initiate engaging dialogues",
            "description": (
                "Starting a conversation with hearing loss begins with choosing the right environment and positioning. "
                "Approach the speaker directly in a well-lit area, position yourself with your better ear towards them, "
                "and openly let conversation partners know how best to communicate with you."
            ),
            "audio_url": "https://cdn.plyr.io/static/demo/Kishi_Bashi_-_It_All_Began_With_a_Burst.mp3",
            "duration_seconds": 180,
        },
        {
            "order": 2,
            "slug": "manage-group-conversations",
            "title": "Manage group conversations",
            "subtitle": "Tactics for dinner tables, family gatherings, and multi-speaker settings",
            "description": (
                "Group conversations are dynamic and fast-moving. Sit near the center of the table with your back "
                "against a wall to eliminate rear acoustic interference. Focus your visual attention on the active speaker "
                "and ask a trusted partner to give brief conversational signposts."
            ),
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
            "duration_seconds": 210,
        },
        {
            "order": 3,
            "slug": "improve-understanding",
            "title": "Improve understanding",
            "subtitle": "Combining auditory clarity with visual cues and hearing aid directional focus",
            "description": (
                "Improve speech intelligibility by combining hearing aid amplification with visual speech cues. "
                "Maintain direct line-of-sight contact, reduce competing background noises before listening, "
                "and switch your hearing aid to directional speech mode in complex acoustic environments."
            ),
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
            "duration_seconds": 195,
        },
        {
            "order": 4,
            "slug": "handle-misunderstandings",
            "title": "Handle misunderstandings",
            "subtitle": "Graceful clarification and rephrasing techniques when speech is missed",
            "description": (
                "When you miss a word or phrase, instead of asking 'What?', politely ask the speaker to rephrase: "
                "'Could you say that in different words?' Rephrased sentences introduce different consonant frequencies "
                "that are often much easier for the auditory cortex to decode."
            ),
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
            "duration_seconds": 165,
        },
        {
            "order": 5,
            "slug": "build-stronger-connections",
            "title": "Build stronger connections",
            "subtitle": "Cultivating deeper social relationships and self-advocacy without auditory fatigue",
            "description": (
                "Building meaningful social connections is the ultimate goal of hearing rehabilitation. "
                "Take short auditory rest breaks during long social gatherings, celebrate daily communication wins, "
                "and advocate for your acoustic needs with family and friends."
            ),
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
            "duration_seconds": 240,
        },
    ]

    for data in DEFAULT_SECTIONS:
        tip = EverydayListeningTip.objects.filter(slug=data['slug']).first()
        if not tip:
            EverydayListeningTip.objects.create(
                order=data['order'],
                slug=data['slug'],
                title=data['title'],
                subtitle=data['subtitle'],
                description=data['description'],
                audio_url=data['audio_url'],
                duration_seconds=data['duration_seconds'],
                is_active=True
            )
        else:
            # Update title and order if existing old dummy data
            tip.title = data['title']
            tip.order = data['order']
            if not tip.audio_file and not tip.audio_url:
                tip.audio_url = data['audio_url']
            tip.save()