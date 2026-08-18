from pathlib import Path
import os
from decouple import config
from datetime import timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ah+qh6%9#=jnm-vw(y9=u3wf5#(30$w%=7#g8xz*r^m&+&l^4z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #third party apps can be added here
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    # coustom apps can be added here
    'users.apps.UsersConfig',
    'legal_pages.apps.LegalPagesConfig',
    'weekly_tutorials.apps.WeeklyTutorialsConfig',
    'learn.apps.LearnConfig',
    'what_normal.apps.WhatNormalConfig',
    'skills_strategies.apps.SkillsStrategiesConfig',
    'device_care.apps.DeviceCareConfig',
    'support_chat.apps.SupportChatConfig',
]

from django.urls import reverse_lazy

UNFOLD = {
    "SITE_TITLE": "Hearing Improvement Admin",
    "SITE_HEADER": "Hearing Improvement Portal",
    "SITE_INDEX_TITLE": "Hearing App Administration",
    "THEME": "auto",
    "SHOW_HISTORY": True,
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Care Team Support Chat",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "User Support Conversations",
                        "icon": "forum",
                        "link": reverse_lazy("admin:support_chat_supportconversation_changelist"),
                    },
                    {
                        "title": "Support Messages & Attachments",
                        "icon": "mark_chat_unread",
                        "link": reverse_lazy("admin:support_chat_supportmessage_changelist"),
                    },
                ],
            },
            {
                "title": "Device Care (Brands, Models & Guides)",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Hearing Aid Brands",
                        "icon": "branding_watermark",
                        "link": reverse_lazy("admin:device_care_hearingaidbrand_changelist"),
                    },
                    {
                        "title": "Hearing Aid Device Models",
                        "icon": "devices",
                        "link": reverse_lazy("admin:device_care_hearingaidmodel_changelist"),
                    },
                    {
                        "title": "Device Care Sections & Guides",
                        "icon": "cleaning_services",
                        "link": reverse_lazy("admin:device_care_devicecaresection_changelist"),
                    },
                    {
                        "title": "Tutorial Videos",
                        "icon": "ondemand_video",
                        "link": reverse_lazy("admin:device_care_devicecarevideo_changelist"),
                    },
                    {
                        "title": "User Wear Time Logs",
                        "icon": "schedule",
                        "link": reverse_lazy("admin:users_hearingaidweartime_changelist"),
                    },
                ],
            },
            {
                "title": "Learn & Daily Lessons",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Welcome Tutorial Video",
                        "icon": "smart_display",
                        "link": reverse_lazy("admin:learn_welcometutorial_changelist"),
                    },
                    {
                        "title": "Check-in Overview Video",
                        "icon": "fact_check",
                        "link": reverse_lazy("admin:learn_checkinoverviewvideo_changelist"),
                    },
                    {
                        "title": "Care Team Support Video",
                        "icon": "medical_services",
                        "link": reverse_lazy("admin:learn_careteamsupportvideo_changelist"),
                    },
                    {
                        "title": "Progress Overview Video",
                        "icon": "insights",
                        "link": reverse_lazy("admin:learn_progressoverviewvideo_changelist"),
                    },
                    {
                        "title": "Daily Lessons (Upload Video & Audio)",
                        "icon": "school",
                        "link": reverse_lazy("admin:learn_dailylesson_changelist"),
                    },
                    {
                        "title": "User Learning Progress",
                        "icon": "auto_graph",
                        "link": reverse_lazy("admin:learn_userlessonprogress_changelist"),
                    },
                ],
            },
            {
                "title": "Skills & Strategies",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Everyday Listening Tips (Audio Upload)",
                        "icon": "hearing",
                        "link": reverse_lazy("admin:skills_strategies_everydaylisteningtip_changelist"),
                    },
                ],
            },
            {
                "title": "What's Normal Section",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "What's Normal Videos",
                        "icon": "video_library",
                        "link": reverse_lazy("admin:what_normal_whatnormalvideo_changelist"),
                    },
                    {
                        "title": "What's Normal Audios",
                        "icon": "library_music",
                        "link": reverse_lazy("admin:what_normal_whatnormalaudio_changelist"),
                    },
                ],
            },
            {
                "title": "Weekly 6-Week Program",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Weekly Tutorials & Tips",
                        "icon": "calendar_view_week",
                        "link": reverse_lazy("admin:weekly_tutorials_weeklytutorial_changelist"),
                    },
                    {
                        "title": "User Weekly Progress",
                        "icon": "date_range",
                        "link": reverse_lazy("admin:weekly_tutorials_userweeklyprogress_changelist"),
                    },
                ],
            },
            {
                "title": "Users & Account Management",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Users Accounts",
                        "icon": "person",
                        "link": reverse_lazy("admin:users_user_changelist"),
                    },
                    {
                        "title": "Daily Check-Ins",
                        "icon": "fact_check",
                        "link": reverse_lazy("admin:users_dailycheckin_changelist"),
                    },
                    {
                        "title": "Onboarding Survey Data",
                        "icon": "assignment",
                        "link": reverse_lazy("admin:users_useronboarding_changelist"),
                    },
                    {
                        "title": "Troubleshooting Tutorials",
                        "icon": "live_help",
                        "link": reverse_lazy("admin:users_checkintutorial_changelist"),
                    },
                    {
                        "title": "Tutorial Feedback",
                        "icon": "feedback",
                        "link": reverse_lazy("admin:users_checkintutorialfeedback_changelist"),
                    },
                    {
                        "title": "Login History",
                        "icon": "history",
                        "link": reverse_lazy("admin:users_userloginhistory_changelist"),
                    },
                    {
                        "title": "Account Deletion Requests",
                        "icon": "delete_forever",
                        "link": reverse_lazy("admin:users_accountdeletionrequest_changelist"),
                    },
                    {
                        "title": "Profile Data Deletion Requests",
                        "icon": "no_accounts",
                        "link": reverse_lazy("admin:users_profiledatadeletionrequest_changelist"),
                    },
                ],
            },
        ],
    },
}



AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Simple JWT Configuration
SIMPLE_JWT = {
    # Token lifetime
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    # Token claims
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    # Token format
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    # Token classes
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    
    # Sliding tokens
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(hours=1),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'users.authentication.FirebaseAuthentication',
    ),
    'EXCEPTION_HANDLER': 'users.exceptions.custom_exception_handler',
}

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH = config('FIREBASE_CREDENTIALS_PATH', default='hearing-improvement-mobile-app-firebase-adminsdk-fbsvc-58093b6492.json')



