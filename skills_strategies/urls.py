from django.urls import path
from .views import (
    StartConversationAudioView,
    ManageGroupConversationsAudioView,
    ImproveUnderstandingAudioView,
    HandleMisunderstandingsAudioView,
    BuildStrongerConnectionsAudioView,
    EverydayListeningTipListView,
    EverydayListeningTipDetailView,
)

app_name = 'skills_strategies'

urlpatterns = [
    # 5 Dedicated Audio GET Endpoints
    path('start-the-conversation/', StartConversationAudioView.as_view(), name='start-the-conversation'),
    path('start-the-converstion/', StartConversationAudioView.as_view(), name='start-the-converstion-alias'),
    path('manage-group-conversations/', ManageGroupConversationsAudioView.as_view(), name='manage-group-conversations'),
    path('improve-understanding/', ImproveUnderstandingAudioView.as_view(), name='improve-understanding'),
    path('handle-misunderstandings/', HandleMisunderstandingsAudioView.as_view(), name='handle-misunderstandings'),
    path('build-stronger-connections/', BuildStrongerConnectionsAudioView.as_view(), name='build-stronger-connections'),

    # List and Detail Endpoints
    path('', EverydayListeningTipListView.as_view(), name='section-list'),
    path('everyday-listening-tips/', EverydayListeningTipListView.as_view(), name='tip-list'),
    path('everyday-listening-tips/<str:lookup>/', EverydayListeningTipDetailView.as_view(), name='tip-detail'),
]