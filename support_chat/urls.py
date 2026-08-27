from django.urls import path
from .views import (
    UserConversationView,
    SendMessageView,
    MarkReadView,
)

app_name = 'support_chat'

urlpatterns = [
    # 1. Get Full Support Chat History
    path('messages/', UserConversationView.as_view(), name='message-list'),
    path('conversation/', UserConversationView.as_view(), name='conversation'),
    path('my-conversation/', UserConversationView.as_view(), name='my-conversation'),

    # 2. Post Message to Support (Text, Picture, Video, Audio, File)
    path('send/', SendMessageView.as_view(), name='send-message'),

    # 3. Mark Support Messages as Read
    path('mark-read/', MarkReadView.as_view(), name='mark-read'),
]