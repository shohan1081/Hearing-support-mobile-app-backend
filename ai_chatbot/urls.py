from django.urls import path
from .views import (
    AIChatView,
    QuickPromptSuggestionsView,
    AIChatSessionListView,
    AIChatSessionDetailView,
    ClearAIChatSessionView,
)

app_name = 'ai_chatbot'

urlpatterns = [
    # Main chat endpoint
    path('chat/', AIChatView.as_view(), name='chat'),
    path('message/', AIChatView.as_view(), name='send-message'),

    # Quick prompt chips for chatbot UI
    path('suggestions/', QuickPromptSuggestionsView.as_view(), name='suggestions'),
    path('quick-prompts/', QuickPromptSuggestionsView.as_view(), name='quick-prompts'),

    # Chat session history & management
    path('sessions/', AIChatSessionListView.as_view(), name='session-list'),
    path('sessions/<uuid:session_id>/', AIChatSessionDetailView.as_view(), name='session-detail'),
    path('clear/', ClearAIChatSessionView.as_view(), name='clear'),
]