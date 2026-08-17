from .models import WeeklyTutorial, UserWeeklyProgress
from django.utils import timezone


def get_or_create_user_progress(user):
    """
    Get or create UserWeeklyProgress record for a user
    Defaults journey_start_date to user's date_joined or today
    """
    progress, created = UserWeeklyProgress.objects.get_or_create(
        user=user,
        defaults={
            'journey_start_date': user.date_joined.date() if hasattr(user, 'date_joined') and user.date_joined else timezone.now().date(),
            'completed_weeks': []
        }
    )
    return progress


def seed_default_weekly_tutorials():
    """
    Populate default 6 weeks tutorials if they do not exist
    """
    DEFAULT_WEEKS = [
        {
            "week_number": 1,
            "title": "Awareness",
            "banner_text": "You're in week 1: Awareness- Your brain is waking up to more sound. This is expected.",
            "description": (
                "Welcome to Week 1 of your hearing journey! During this first week, your auditory cortex is "
                "adapting to environmental sounds you may not have heard clearly for a long time. You might notice "
                "background sounds like refrigerator hums, footsteps, or clock ticking seem louder than expected. "
                "This is completely normal as your brain recalibrates to full-spectrum hearing."
            ),
            "what_you_will_learn": [
                "Understanding how your brain adapts to new sounds",
                "What to expect during the first 7 days",
                "Building a consistent daily wearing schedule",
                "Managing initial acoustic fatigue"
            ]
        },
        {
            "week_number": 2,
            "title": "Adjustment",
            "banner_text": "You're in week 2: Adjustment- Environment sounds are still noticeable.This is often the hardest week, but it is temporary.",
            "description": (
                "Welcome to Week 2! This week focuses on adjusting to ambient background noise. Many users find "
                "Week 2 the most challenging because your brain is actively sorting through environmental sounds. "
                "Stay persistent—your brain will naturally begin to filter out non-essential background noise over the coming days."
            ),
            "what_you_will_learn": [
                "Navigating environmental noise sensitivity",
                "Techniques to handle background noise overload",
                "Why week 2 feels challenging and how to push through",
                "Adjusting volume controls safely"
            ]
        },
        {
            "week_number": 3,
            "title": "Acclimation",
            "banner_text": "You're in week 3: Acclimation- Speech is becoming clearer in quiet settings. Keep practicing.",
            "description": (
                "Welcome to Week 3! By now, background sounds are starting to feel more natural. This week, "
                "your focus shifts to one-on-one conversations in quiet settings and listening to audio from devices like TV or phone."
            ),
            "what_you_will_learn": [
                "Improving speech comprehension in quiet spaces",
                "Active listening strategies with family and friends",
                "Optimizing TV and phone audio clarity",
                "Recognizing subtle sound nuances"
            ]
        },
        {
            "week_number": 4,
            "title": "Complex Environments",
            "banner_text": "You're in week 4: Complex Environments- Hearing in noisy places like restaurants is improving step by step.",
            "description": (
                "Welcome to Week 4! Now you are ready to challenge your hearing in multi-talker and noisy environments "
                "such as restaurants, family gatherings, or outdoor events."
            ),
            "what_you_will_learn": [
                "Strategies for understanding speech in noise",
                "Positioning yourself for optimal hearing in group settings",
                "Using directional microphones and noise suppression features",
                "Reducing listening strain during social gatherings"
            ]
        },
        {
            "week_number": 5,
            "title": "Refinement",
            "banner_text": "You're in week 5: Refinement- Fine-tuning your daily routines and personal sound preferences.",
            "description": (
                "Welcome to Week 5! You are now comfortable in most hearing environments. This week focuses on "
                "fine-tuning your experience and communicating any remaining challenges with your hearing specialist."
            ),
            "what_you_will_learn": [
                "Identifying subtle sound preference adjustments",
                "Effective communication with your audiologist/specialist",
                "Customizing program settings for music and outdoors",
                "Maximizing listening comfort in complex settings"
            ]
        },
        {
            "week_number": 6,
            "title": "Mastery",
            "banner_text": "You're in week 6: Mastery- You have successfully built a long-term habit for clearer hearing!",
            "description": (
                "Congratulations on reaching Week 6! You have completed the foundational acclimation journey. "
                "Your brain has successfully adapted to enhanced sound processing, giving you clearer hearing and renewed confidence."
            ),
            "what_you_will_learn": [
                "Maintaining your hearing health long-term",
                "Daily cleaning and care for device longevity",
                "Tracking ongoing progress and scheduling checkups",
                "Celebrating your hearing transformation success"
            ]
        }
    ]

    for data in DEFAULT_WEEKS:
        WeeklyTutorial.objects.get_or_create(
            week_number=data['week_number'],
            defaults={
                'title': data['title'],
                'banner_text': data['banner_text'],
                'description': data['description'],
                'what_you_will_learn': data['what_you_will_learn'],
                'is_active': True
            }
        )
