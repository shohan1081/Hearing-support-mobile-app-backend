from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class AIChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_chatbot'
    verbose_name = _('AI Hearing Assistant Chatbot')
