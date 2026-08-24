import json
import logging
import requests
from django.conf import settings
from django.utils import timezone
from .models import AIChatSession, AIChatMessage

logger = logging.getLogger(__name__)


def build_user_hearing_context(user):
    """
    Build a real-time clinical and activity context snapshot for the user
    """
    context = {
        "user_name": user.get_full_name() or user.name or "User",
        "user_email": user.email,
        "daily_goal_hours": getattr(user, 'daily_wear_goal', 8) or 8,
        "hearing_score": 50,
        "hearing_score_breakdown": {},
        "today_wear_hours": 0.0,
        "today_wear_minutes": 0,
        "past_7_days_avg_wear_hours": 0.0,
        "latest_checkin_status": "none",
        "latest_checkin_notes": "",
        "current_week": 1,
        "completed_lessons_count": 0,
        "onboarding_challenges": [],
    }

    try:
        # 1. Hearing Score calculation
        from users.views import calculate_user_hearing_score
        context["hearing_score"] = round(calculate_user_hearing_score(user), 1)
    except Exception as e:
        logger.debug(f"Error calculating hearing score in AI context: {e}")

    try:
        # 2. Wear Time info
        from users.models import HearingAidWearTime
        today = timezone.now().date()
        today_log = HearingAidWearTime.objects.filter(user=user, date=today).first()
        if today_log:
            context["today_wear_hours"] = round(today_log.total_hours, 1)
            context["today_wear_minutes"] = (today_log.hours * 60) + today_log.minutes

        seven_days_ago = today - timezone.timedelta(days=7)
        past_logs = HearingAidWearTime.objects.filter(user=user, date__gte=seven_days_ago)
        if past_logs.exists():
            total_h = sum([log.total_hours for log in past_logs])
            context["past_7_days_avg_wear_hours"] = round(total_h / max(past_logs.count(), 1), 1)
    except Exception as e:
        logger.debug(f"Error retrieving wear time in AI context: {e}")

    try:
        # 3. Latest Check-in
        from users.models import DailyCheckIn
        latest_checkin = DailyCheckIn.objects.filter(user=user).order_by('-checkin_date', '-created_at').first()
        if latest_checkin:
            context["latest_checkin_status"] = latest_checkin.hearing_status
            context["latest_checkin_notes"] = (
                latest_checkin.what_went_well or
                latest_checkin.what_went_okay or
                latest_checkin.why_struggling or
                ""
            )
    except Exception as e:
        logger.debug(f"Error retrieving check-in in AI context: {e}")

    try:
        # 4. Weekly Program Progress
        from weekly_tutorials.models import UserWeeklyProgress
        prog = UserWeeklyProgress.objects.filter(user=user).first()
        if prog:
            context["current_week"] = prog.current_week
    except Exception as e:
        logger.debug(f"Error retrieving weekly progress in AI context: {e}")

    try:
        # 5. Onboarding Preferences
        from users.models import UserOnboarding
        onb = UserOnboarding.objects.filter(user=user).first()
        if onb and onb.challenges_faced:
            context["onboarding_challenges"] = onb.challenges_faced if isinstance(onb.challenges_faced, list) else [str(onb.challenges_faced)]
    except Exception as e:
        logger.debug(f"Error retrieving onboarding in AI context: {e}")

    return context


def get_ai_system_prompt(user_context):
    """
    Generate rich system prompt tailored with live user metrics and app features
    """
    name = user_context.get("user_name", "User")
    hearing_score = user_context.get("hearing_score", 50)
    today_wear = user_context.get("today_wear_hours", 0.0)
    goal = user_context.get("daily_goal_hours", 8)
    avg_wear = user_context.get("past_7_days_avg_wear_hours", 0.0)
    checkin_status = user_context.get("latest_checkin_status", "none")
    current_week = user_context.get("current_week", 1)
    challenges = ", ".join(user_context.get("onboarding_challenges", [])) or "Hearing adaptation"

    prompt = f"""You are the friendly, empathetic, and knowledgeable AI Hearing Care & App Assistant in the Hearing Improvement Mobile App.
Your role is to support the user in their hearing rehabilitation journey, answer questions about hearing improvement, explain app features, and provide practical auditory exercises.

USER'S LIVE PROFILE & ACTIVITY METRICS:
- Name: {name}
- Overall Hearing Score: {hearing_score} / 100
- Today's Hearing Aid Wear Time: {today_wear} hours (Daily Target Goal: {goal} hours)
- 7-Day Average Wear Time: {avg_wear} hours/day
- Current Weekly Rehabilitation Program: Week {current_week} of 6
- Latest Daily Check-in Mood/Status: {checkin_status}
- Self-reported Challenges: {challenges}

CORE APP FEATURES YOU CAN GUIDE THE USER TO:
1. Daily Check-in & Symptoms Tracker (/api/users/checkin/): Log daily mood (Good, Okay, Struggling, Frustrated).
2. Check-in Video Tutorials (/api/users/checkin-tutorials/): 7 video guides for loud sounds, background noise, speech clarity, restaurants, TV clarity, and fatigue.
3. Wear Time & Hearing Score (/api/users/wear-time/, /api/users/hearing-score/): Track daily hours towards their {goal}h goal.
4. 6-Week Rehabilitation Program (/api/weekly-tutorials/): Structured weekly milestones and active listening tips.
5. Daily Lessons & Audio Training (/api/learn/): Everyday cognitive and auditory exercises.
6. What's Normal Section (/api/what-normal/): Audio/video guidance normalizing early adaptation sensations.
7. Device Care & Troubleshooting (/api/device-care/): Cleaning, wax filter change, and Bluetooth guides.
8. Care Team Consultations & Appointments (/api/users/appointments/request/): User can request direct consultations with a care specialist.
9. Report an Issue (/api/users/issues/report/): Report sound quality, Bluetooth, battery, or hardware issues.

EXPERT GUIDANCE RULES:
- If user asks about their progress ("tell me about my progress", "how am I doing?"): Quote their exact live metrics ({hearing_score}/100 Hearing Score, {today_wear}h today, {avg_wear}h weekly avg) and give specific, encouraging praise and actionable next steps.
- If user asks how to improve their Hearing Score: Explain the 4 Pillars of the Hearing Score: (1) Consistent daily wear (8+ hrs/day), (2) Daily learning lesson completion, (3) Daily symptom check-ins, and (4) Listening habit engagement.
- If user asks about noisy environments or restaurants: Provide practical strategies (sit with back against wall in restaurants, turn on speech-in-noise mode, practice active focused listening, position conversational partner on the better ear side).
- If user is struggling with tinnitus: Provide compassionate, reassuring guidance (sound enrichment with low ambient music or white noise, avoiding dead silence, stress reduction, deep breathing, reminder that brain habituates over time).
- Tone: Warm, supportive, encouraging, professional, concise, and formatted clearly with bullet points.
- Medical safety: If user mentions sudden acute hearing loss, physical ear pain, or fluid discharge, recommend consulting an ENT or audiologist immediately.
"""
    return prompt


def call_openai_chat(messages, model=None, temperature=0.7, max_tokens=800):
    """
    Direct HTTP call to OpenAI Chat API using requests
    """
    api_key = getattr(settings, 'OPENAI_API_KEY', '') or ''
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured in settings.")

    selected_model = model or getattr(settings, 'OPENAI_CHAT_MODEL', 'gpt-4o-mini') or 'gpt-4o-mini'

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": selected_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code != 200:
        logger.error(f"OpenAI API Error ({response.status_code}): {response.text}")
        raise RuntimeError(f"OpenAI API Error ({response.status_code}): {response.text}")

    data = response.json()
    reply_text = data['choices'][0]['message']['content'].strip()
    tokens = data.get('usage', {}).get('total_tokens', 0)
    return reply_text, selected_model, tokens


def generate_smart_fallback_response(prompt, user_context):
    """
    High-quality expert fallback when OpenAI API key is not configured or offline
    """
    p_lower = prompt.lower().strip()
    name = user_context.get("user_name", "there")
    score = user_context.get("hearing_score", 50)
    today_wear = user_context.get("today_wear_hours", 0.0)
    goal = user_context.get("daily_goal_hours", 8)
    avg_wear = user_context.get("past_7_days_avg_wear_hours", 0.0)
    current_week = user_context.get("current_week", 1)

    # 1. Progress & Status
    if any(k in p_lower for k in ['progress', 'how am i doing', 'my stats', 'summary', 'report', 'wear time']):
        return (
            f"Here is your current progress summary, {name}!\n\n"
            f"📊 **Current Hearing Score**: **{score} / 100**\n"
            f"⏱️ **Today's Wear Time**: **{today_wear} hours** (Daily Goal: {goal} hours)\n"
            f"📈 **7-Day Average**: **{avg_wear} hours/day**\n"
            f"🗓️ **Rehabilitation Milestone**: **Week {current_week} of 6**\n\n"
            f"💡 **Key Tip**: Increasing your daily wear time towards {goal} hours is the fastest way to retrain your auditory cortex and improve your Hearing Score. Keep up the great work!"
        )

    # 2. Hearing Score Improvement
    if any(k in p_lower for k in ['hearing score', 'improve my score', 'increase score', 'higher score']):
        return (
            f"To boost your Hearing Score from **{score}/100**, focus on these 4 pillars:\n\n"
            f"1. ⏱️ **Consistent Daily Wear (40 pts)**: Wear your hearing devices for **{goal}+ hours per day**. Currently, you have logged **{today_wear}h today** (avg {avg_wear}h/day).\n"
            f"2. 🎧 **Daily Auditory Lessons (30 pts)**: Complete your daily lessons in the **Learn** tab to exercise speech discrimination.\n"
            f"3. 📋 **Daily Symptom Check-ins (20 pts)**: Submit your daily check-in so we can adapt troubleshooting tips.\n"
            f"4. 💡 **Skills & Strategy Practice (10 pts)**: Listen to our everyday listening tips and device care guides.\n\n"
            f"Every hour of consistent wear helps your brain adapt to new sound frequencies!"
        )

    # 3. Noisy Environments & Restaurants
    if any(k in p_lower for k in ['noisy', 'noise', 'restaurant', 'crowd', 'background noise', 'exercise', 'dinner']):
        return (
            f"Handling background noise in restaurants and social settings is one of the most important hearing skills! Here are 4 proven exercises:\n\n"
            f"1. 🪑 **Strategic Seating**: Sit with your back against the wall or corner. This prevents background noise from entering from behind you.\n"
            f"2. 🎯 **Directional Microphone Focus**: In your hearing aid settings, activate the **'Speech in Noise'** or directional focus program.\n"
            f"3. 👁️ **Visual Speech Cues**: Maintain good eye contact and face the speaker directly in well-lit areas to utilize natural lip-reading cues.\n"
            f"4. 📻 **Home Auditory Training**: Practice listening to an audiobook or news podcast while playing soft instrumental music or TV background noise at low volume.\n\n"
            f"Check out our tutorial video **'Restaurants Are Hard'** in the Check-in Tutorials section for more step-by-step techniques!"
        )

    # 4. Tinnitus Support
    if any(k in p_lower for k in ['tinnitus', 'ringing', 'buzzing', 'hissing', 'ear sound']):
        return (
            f"I understand dealing with tinnitus can feel exhausting, {name}. Here are clinically recommended steps you can take right now for relief:\n\n"
            f"1. 🌊 **Sound Enrichment**: Avoid dead silence. Play gentle ambient sounds, nature sounds (rain, ocean waves), or a low fan to reduce the contrast of the ringing.\n"
            f"2. 🦻 **Keep Wearing Your Hearing Aids**: Hearing aids amplify ambient room sounds, which naturally mask the tinnitus signals in your auditory pathway.\n"
            f"3. 🧘 **Deep Breathing & Relaxation**: Tinnitus is amplified by autonomic stress. Taking 5 minutes of slow belly breathing can calm nervous system reactivity.\n"
            f"4. 📅 **Audiologist Consultation**: If your tinnitus suddenly changes or feels overwhelming, you can request a **Care Consultation** directly in the app to speak with an audiologist.\n\n"
            f"Remember, tinnitus perception fluctuates daily, and your brain gradually habituates with sound enrichment."
        )

    # 5. Device Care, Cleaning & Bluetooth
    if any(k in p_lower for k in ['clean', 'wax', 'filter', 'bluetooth', 'connect', 'pair', 'battery', 'charge']):
        return (
            f"Here are quick tips for your hearing aid maintenance and connectivity:\n\n"
            f"🧹 **Cleaning & Wax Filter**:\n"
            f"- Wipe your domes daily with a clean, dry microfiber cloth.\n"
            f"- If sound feels weak or muffled, inspect the white wax guard filter at the tip and replace it if blocked.\n\n"
            f"📶 **Bluetooth Pairing**:\n"
            f"- Turn your hearing aids off and on to place them in pairing mode for 3 minutes.\n"
            f"- Open your phone's Bluetooth settings, select your hearing aids, and tap 'Pair'.\n\n"
            f"Explore the full **Device Care** section in the app for model-specific video guides!"
        )

    # Default General Support
    return (
        f"Hello {name}! I am your AI Hearing Assistant.\n\n"
        f"I can help you with:\n"
        f"• 📊 **Your Progress & Hearing Score** (Currently {score}/100)\n"
        f"• 🔊 **Strategies for Noisy Environments & Restaurants**\n"
        f"• 🧘 **Tinnitus Management & Sound Relief**\n"
        f"• 🦻 **Hearing Aid Adaptation & Daily Wear Goals** ({today_wear}h logged today)\n"
        f"• 🛠️ **Device Care, Cleaning, and App Guides**\n\n"
        f"How can I assist your hearing journey today?"
    )


def generate_ai_chat_response(user, message_text, session_id=None):
    """
    Main entry point: generates AI response using OpenAI with user context & fallback
    """
    session = None
    if session_id:
        try:
            session = AIChatSession.objects.filter(session_id=session_id, user=user).first()
        except Exception:
            pass

    if not session:
        title_snippet = message_text[:40] if len(message_text) <= 40 else message_text[:37] + "..."
        session = AIChatSession.objects.create(
            user=user,
            title=title_snippet,
            is_active=True
        )

    # Save user message
    user_msg = AIChatMessage.objects.create(
        session=session,
        sender=AIChatMessage.SENDER_USER,
        message_text=message_text
    )

    # Build user context
    user_context = build_user_hearing_context(user)
    system_prompt = get_ai_system_prompt(user_context)

    # Prepare OpenAI message payload
    messages_payload = [
        {"role": "system", "content": system_prompt}
    ]

    # Add recent history (up to last 10 messages)
    recent_history = session.get_recent_history(limit=10)
    for msg in recent_history:
        role = "user" if msg.sender == AIChatMessage.SENDER_USER else "assistant"
        messages_payload.append({"role": role, "content": msg.message_text})

    # Add current user message
    messages_payload.append({"role": "user", "content": message_text})

    # Call OpenAI or Fallback
    ai_reply = ""
    model_used = "gpt-4o-mini"
    tokens = 0

    try:
        ai_reply, model_used, tokens = call_openai_chat(messages_payload)
    except Exception as e:
        logger.warning(f"OpenAI call failed or key missing ({e}), using smart domain fallback.")
        ai_reply = generate_smart_fallback_response(message_text, user_context)
        model_used = "domain-expert-fallback"

    # Save assistant message
    ai_msg = AIChatMessage.objects.create(
        session=session,
        sender=AIChatMessage.SENDER_ASSISTANT,
        message_text=ai_reply,
        context_snapshot=user_context,
        model_name=model_used,
        tokens_used=tokens
    )

    session.last_interaction_at = timezone.now()
    session.save(update_fields=['last_interaction_at', 'updated_at'])

    return {
        "session_id": str(session.session_id),
        "session_title": session.title,
        "user_message": message_text,
        "ai_response": ai_reply,
        "model_used": model_used,
        "tokens_used": tokens,
        "user_stats_snapshot": {
            "hearing_score": user_context.get("hearing_score", 50),
            "today_wear_time_hours": user_context.get("today_wear_hours", 0.0),
            "daily_goal_hours": user_context.get("daily_goal_hours", 8),
            "past_7_days_avg_wear_hours": user_context.get("past_7_days_avg_wear_hours", 0.0),
            "weekly_progress_week": user_context.get("current_week", 1),
            "latest_checkin_status": user_context.get("latest_checkin_status", "none")
        },
        "created_at": ai_msg.created_at.isoformat()
    }