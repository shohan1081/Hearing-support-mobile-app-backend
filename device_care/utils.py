from .models import HearingAidBrand, HearingAidModel, DeviceCareSection, DeviceCareVideo


def seed_default_device_care_data():
    """
    Populate default sample brands, models, sections, and videos for Device Care if none exist
    """
    if HearingAidBrand.objects.exists():
        return

    # 1. Phonak Brand
    phonak = HearingAidBrand.objects.create(
        name="Phonak",
        slug="phonak",
        description="Leading manufacturer of innovative hearing aids and wireless accessories.",
        order=1,
        is_active=True
    )

    # Phonak Audéo Lumity Model
    audeo_lumity = HearingAidModel.objects.create(
        brand=phonak,
        name="Audéo Lumity",
        slug="audeo-lumity",
        description="Advanced rechargeable hearing aid with SmartSpeech technology and direct Bluetooth connectivity.",
        user_manual_url="https://www.phonak.com/en-us/support/user-guides",
        order=1,
        is_active=True
    )

    # Section 1: Cleaning Guide
    cleaning_section = DeviceCareSection.objects.create(
        model=audeo_lumity,
        section_type=DeviceCareSection.SECTION_CLEANING_GUIDE,
        title="Daily & Weekly Cleaning Guide",
        subtitle="Keep your Audéo Lumity receivers and ear domes free from earwax and debris",
        content_text=(
            "1. Daily: Wipe the hearing aid and dome with a soft, dry tissue or microfiber cloth.\n"
            "2. Never use water, alcohol, or household cleaners on your hearing aids.\n"
            "3. Inspect the CeruShield wax guard daily. If plugged, replace the wax guard using the tool.\n"
            "4. Weekly: Brush microphone ports gently with the provided cleaning brush."
        ),
        order=1,
        is_active=True
    )

    # Videos for Cleaning Guide
    DeviceCareVideo.objects.create(
        section=cleaning_section,
        title="How to Change CeruShield Wax Guard",
        description="Step-by-step video demonstration on replacing wax filters on Phonak Audéo Lumity receivers.",
        video_file="https://www.w3schools.com/html/mov_bbb.mp4",
        duration_seconds=140,
        order=1,
        is_active=True
    )
    DeviceCareVideo.objects.create(
        section=cleaning_section,
        title="Cleaning Earpieces & Receiver Domes",
        description="Learn how to detach and clean silicone domes safely without damaging the receiver wire.",
        video_file="https://www.w3schools.com/html/mov_bbb.mp4",
        duration_seconds=160,
        order=2,
        is_active=True
    )

    # Section 2: Care Tips
    care_section = DeviceCareSection.objects.create(
        model=audeo_lumity,
        section_type=DeviceCareSection.SECTION_CARE_TIPS,
        title="General Care & Storage Tips",
        subtitle="Protect your hearing aids from moisture, heat, and physical damage",
        content_text=(
            "1. Store in charger or dry box when not in use.\n"
            "2. Keep hearing aids away from pets and small children.\n"
            "3. Remove devices before swimming, showering, or applying hairspray/perfume.\n"
            "4. Avoid exposing hearing aids to direct heat sources like radiators or car dashboards."
        ),
        order=2,
        is_active=True
    )
    DeviceCareVideo.objects.create(
        section=care_section,
        title="Using Phonak Charger Case & Drying Capsule",
        description="Proper charging techniques and dehumidifier capsule usage.",
        video_file="https://www.w3schools.com/html/mov_bbb.mp4",
        duration_seconds=120,
        order=1,
        is_active=True
    )

    # Section 3: Troubleshooting
    trouble_section = DeviceCareSection.objects.create(
        model=audeo_lumity,
        section_type=DeviceCareSection.SECTION_TROUBLESHOOTING,
        title="Common Troubleshooting Solutions",
        subtitle="Quick fixes for weak sound, static noise, or charging issues",
        content_text=(
            "1. No Sound / Weak Sound: Check if receiver dome is blocked with wax. Replace wax guard.\n"
            "2. Whistling / Feedback: Ensure ear dome is inserted correctly and securely in ear canal.\n"
            "3. Bluetooth Disconnected: Turn phone Bluetooth off and on, or restart hearing aids.\n"
            "4. Not Charging: Clean gold charging contacts on hearing aid and inside charger base."
        ),
        order=3,
        is_active=True
    )
    DeviceCareVideo.objects.create(
        section=trouble_section,
        title="Troubleshooting Weak Sound & Resetting Device",
        description="Quick diagnostic steps to resolve common audio dropouts.",
        video_file="https://www.w3schools.com/html/mov_bbb.mp4",
        duration_seconds=180,
        order=1,
        is_active=True
    )

    # Section 4: User Manual
    DeviceCareSection.objects.create(
        model=audeo_lumity,
        section_type=DeviceCareSection.SECTION_USER_MANUAL,
        title="Phonak Audéo Lumity Official User Manual",
        subtitle="Access full official digital user guide & safety documentation",
        content_text="Click the link below to view or download the complete official Phonak user manual.",
        manual_url="https://www.phonak.com/en-us/support/user-guides",
        order=4,
        is_active=True
    )

    # 2. Oticon Brand
    oticon = HearingAidBrand.objects.create(
        name="Oticon",
        slug="oticon",
        description="BrainHearing technology pioneer creating natural sound experiences.",
        order=2,
        is_active=True
    )

    oticon_more = HearingAidModel.objects.create(
        brand=oticon,
        name="Oticon More 1",
        slug="oticon-more-1",
        description="Deep Neural Network powered hearing aid for clear speech clarity.",
        user_manual_url="https://www.oticon.com/support/user-guides",
        order=1,
        is_active=True
    )

    # Oticon Cleaning Guide
    oticon_clean = DeviceCareSection.objects.create(
        model=oticon_more,
        section_type=DeviceCareSection.SECTION_CLEANING_GUIDE,
        title="Oticon More Cleaning & Maintenance",
        subtitle="Daily cleaning steps for Oticon ProWax wax filter and domes",
        content_text="Wipe daily with soft dry cloth and replace ProWax filter when clogged.",
        order=1,
        is_active=True
    )
    DeviceCareVideo.objects.create(
        section=oticon_clean,
        title="Replacing Oticon ProWax Filter",
        description="Demonstration on replacing ProWax miniFit filters.",
        video_file="https://www.w3schools.com/html/mov_bbb.mp4",
        duration_seconds=130,
        order=1,
        is_active=True
    )
