from .models import EverydayListeningTip


def seed_default_everyday_listening_tips():
    """
    Populate all 15 official Skills & Strategies audio sections across the 3 categories:
    1. Everyday Listening Tips (5 audios)
    2. Communication Strategies (5 audios)
    3. Building Confidence (5 audios)
    """
    ALL_SECTIONS = [
        # ==========================================
        # 1. Everyday Listening Tips (5 audios)
        # ==========================================
        {
            "category": EverydayListeningTip.CATEGORY_EVERYDAY_LISTENING,
            "order": 1,
            "slug": "reduce-background-noise",
            "title": "Reduce background noise",
            "subtitle": "Minimize ambient acoustic distractions before starting conversations",
            "description": (
                "Background noise can make speech discrimination significantly harder. Before beginning a conversation, "
                "lower the volume on televisions, move away from loud appliances like dishwashers or fans, "
                "and choose quiet seating areas away from kitchen doors in restaurants."
            ),
            "audio_url": "https://cdn.plyr.io/static/demo/Kishi_Bashi_-_It_All_Began_With_a_Burst.mp3",
            "duration_seconds": 120,
        },
        {
            "category": EverydayListeningTip.CATEGORY_EVERYDAY_LISTENING,
            "order": 2,
            "slug": "face-the-speaker",
            "title": "Face the speaker",
            "subtitle": "Position yourself directly facing whoever is speaking",
            "description": (
                "Direct line-of-sight visual contact improves sound reception and allows your brain to combine "
                "auditory cues with lip-reading and facial expressions. Always ensure you are in the same room "
                "and facing the person talking to you."
            ),
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
            "duration_seconds": 135,
        },
        {
            "category": EverydayListeningTip.CATEGORY_EVERYDAY_LISTENING,
            "order": 3,
            "slug": "take-breaks",
            "title": "Take breaks",
            "subtitle": "Give your auditory cortex short rest periods during noisy days",
            "description": (
                "Listening in complex soundscapes requires heightened mental effort. If you feel tired or overwhelmed, "
                "step into a quiet room for 5 to 10 minutes to let your auditory brain relax and recharge."
            ),
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
            "duration_seconds": 150,
        },
        {
            "category": EverydayListeningTip.CATEGORY_EVERYDAY_LISTENING,
            "order": 4,
            "slug": "use-visual-cues",
            "title": "Use visual cues",
            "subtitle": "Leverage body language, gestures, and facial expressions",
            "description": (
                "Visual cues provide essential context to speech comprehension. Pay attention to hand gestures, "
                "body posture, and lip movements to help fill in missing speech sounds seamlessly."
            ),
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
            "duration_seconds": 140,
        },
        {
            "category": EverydayListeningTip.CATEGORY_EVERYDAY_LISTENING,
            "order": 5,
            "slug": "ask-for-repetition",
            "title": "Ask for repetition",
            "subtitle": "Politely ask speakers to rephrase or speak clearly",
            "description": (
                "If you miss a word or phrase, ask the speaker to rephrase the sentence rather than just repeating "
                "it louder. Rephrased wording often uses different speech frequencies that are easier to understand."
            ),
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
            "duration_seconds": 160,
        },

        # ==========================================
        # 2. Communication Strategies (5 audios)
        # ==========================================
        {
            "category": EverydayListeningTip.CATEGORY_COMMUNICATION_STRATEGIES,
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
            "category": EverydayListeningTip.CATEGORY_COMMUNICATION_STRATEGIES,
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
            "category": EverydayListeningTip.CATEGORY_COMMUNICATION_STRATEGIES,
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
            "category": EverydayListeningTip.CATEGORY_COMMUNICATION_STRATEGIES,
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
            "category": EverydayListeningTip.CATEGORY_COMMUNICATION_STRATEGIES,
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

        # ==========================================
        # 3. Building Confidence (5 audios)
        # ==========================================
        {
            "category": EverydayListeningTip.CATEGORY_BUILDING_CONFIDENCE,
            "order": 1,
            "slug": "start-small",
            "title": "Start small",
            "subtitle": "Begin auditory challenges in low-noise, one-on-one environments",
            "description": (
                "Rebuilding listening confidence is a gradual process. Begin by practicing active listening in calm, "
                "one-on-one settings with close family members before stepping into complex acoustic soundscapes like parties or malls."
            ),
            "audio_url": "https://cdn.plyr.io/static/demo/Kishi_Bashi_-_It_All_Began_With_a_Burst.mp3",
            "duration_seconds": 150,
        },
        {
            "category": EverydayListeningTip.CATEGORY_BUILDING_CONFIDENCE,
            "order": 2,
            "slug": "prepare-before-conversations",
            "title": "Prepare before conversations",
            "subtitle": "Anticipate acoustic environments, topics, and seating arrangements",
            "description": (
                "Preparation removes conversational anxiety. Before attending meetings or social dinners, check the venue layout, "
                "review agenda topics or current events, and arrive slightly early to secure optimal seating."
            ),
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
            "duration_seconds": 175,
        },
        {
            "category": EverydayListeningTip.CATEGORY_BUILDING_CONFIDENCE,
            "order": 3,
            "slug": "be-patient-with-yourself",
            "title": "Be patient with yourself",
            "subtitle": "Understanding auditory brain retraining and emotional resilience",
            "description": (
                "Adapting to hearing aids and speech rehabilitation takes weeks of neuroplastic reorganization. "
                "It is completely normal to have days with auditory fatigue. Treat yourself with compassion and celebrate progress."
            ),
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
            "duration_seconds": 160,
        },
        {
            "category": EverydayListeningTip.CATEGORY_BUILDING_CONFIDENCE,
            "order": 4,
            "slug": "practice-every-day",
            "title": "Practice every day",
            "subtitle": "Consistency in daily wear time and active speech listening",
            "description": (
                "Consistent daily practice reinforces neural pathways. Wearing your hearing devices for your target daily goal "
                "and listening to audiobooks, podcasts, or radio broadcasts daily accelerates speech clarity."
            ),
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
            "duration_seconds": 190,
        },
        {
            "category": EverydayListeningTip.CATEGORY_BUILDING_CONFIDENCE,
            "order": 5,
            "slug": "celebrate-progress",
            "title": "Celebrate progress",
            "subtitle": "Recognizing hearing milestones, improved clarity, and social engagement",
            "description": (
                "Acknowledge every step forward—whether it is enjoying a phone call, understanding grandchildren clearly, "
                "or navigating a restaurant with ease. Every milestone reflects real auditory brain improvement."
            ),
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
            "duration_seconds": 180,
        },
    ]

    for data in ALL_SECTIONS:
        tip = EverydayListeningTip.objects.filter(slug=data['slug']).first()
        if not tip:
            EverydayListeningTip.objects.create(
                category=data['category'],
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
            tip.category = data['category']
            tip.title = data['title']
            tip.order = data['order']
            tip.subtitle = data['subtitle']
            tip.description = data['description']
            if not tip.audio_file and not tip.audio_url:
                tip.audio_url = data['audio_url']
            tip.save()