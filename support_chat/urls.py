from django.urls import path
from .views import (
    UserConversationView,
    SendMessageView,
    MessageListView,
    MarkReadView,
    UnreadCountView,
    AdminConversationListView,
    AdminReplyView,
)

app_name = 'support_chat'

urlpatterns = [
    # Mobile User Support Chat APIs
    path('my-conversation/', UserConversationView.as_view(), name='my-conversation'),
    path('send/', SendMessageView.as_view(), name='send-message'),
    path('messages/', MessageListView.as_view(), name='message-list'),
    path('mark-read/', MarkReadView.as_view(), name='mark-read'),
    path('unread-count/', UnreadCountView.as_view(), name='unread-count'),

    # Care Team Admin APIs
    path('admin/conversations/', AdminConversationListView.as_view(), name='admin-conversations'),
    path('admin/reply/', AdminReplyView.as_view(), name='admin-reply'),
]
