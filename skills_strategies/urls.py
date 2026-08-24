from django.urls import path
from .views import (
    SkillsStrategiesOverviewView,
    EverydayListeningTipsListView,
    CommunicationStrategiesListView,
    BuildingConfidenceListView,
    PracticeAndProgressView,
    # 1. Everyday Listening Tips
    ReduceBackgroundNoiseAudioView,
    FaceTheSpeakerAudioView,
    TakeBreaksAudioView,
    UseVisualCuesAudioView,
    AskForRepetitionAudioView,
    # 2. Communication Strategies
    StartConversationAudioView,
    ManageGroupConversationsAudioView,
    ImproveUnderstandingAudioView,
    HandleMisunderstandingsAudioView,
    BuildStrongerConnectionsAudioView,
    # 3. Building Confidence
    StartSmallAudioView,
    PrepareBeforeConversationsAudioView,
    BePatientWithYourselfAudioView,
    PracticeEveryDayAudioView,
    CelebrateProgressAudioView,
    # Detail lookup
    EverydayListeningTipDetailView,
)

app_name = 'skills_strategies'

urlpatterns = [
    # Main Overview Endpoint
    path('', SkillsStrategiesOverviewView.as_view(), name='overview'),
    path('overview/', SkillsStrategiesOverviewView.as_view(), name='overview-alias'),

    # ========================================================
    # 1. Everyday Listening Tips (List + 5 Dedicated Audio URLs)
    # ========================================================
    path('everyday-listening-tips/', EverydayListeningTipsListView.as_view(), name='everyday-listening-tips-list'),
    path('everyday-listening-tips/reduce-background-noise/', ReduceBackgroundNoiseAudioView.as_view(), name='reduce-background-noise'),
    path('everyday-listening-tips/face-the-speaker/', FaceTheSpeakerAudioView.as_view(), name='face-the-speaker'),
    path('everyday-listening-tips/take-breaks/', TakeBreaksAudioView.as_view(), name='take-breaks'),
    path('everyday-listening-tips/use-visual-cues/', UseVisualCuesAudioView.as_view(), name='use-visual-cues'),
    path('everyday-listening-tips/ask-for-repetition/', AskForRepetitionAudioView.as_view(), name='ask-for-repetition'),

    # ========================================================
    # 2. Communication Strategies (List + 5 Dedicated Audio URLs)
    # ========================================================
    path('communication-strategies/', CommunicationStrategiesListView.as_view(), name='communication-strategies-list'),
    path('communication-strategies/start-the-conversation/', StartConversationAudioView.as_view(), name='comm-start-the-conversation'),
    path('communication-strategies/manage-group-conversations/', ManageGroupConversationsAudioView.as_view(), name='comm-manage-group-conversations'),
    path('communication-strategies/improve-understanding/', ImproveUnderstandingAudioView.as_view(), name='comm-improve-understanding'),
    path('communication-strategies/handle-misunderstandings/', HandleMisunderstandingsAudioView.as_view(), name='comm-handle-misunderstandings'),
    path('communication-strategies/build-stronger-connections/', BuildStrongerConnectionsAudioView.as_view(), name='comm-build-stronger-connections'),

    # ========================================================
    # 3. Building Confidence (List + 5 Dedicated Audio URLs)
    # ========================================================
    path('building-confidence/', BuildingConfidenceListView.as_view(), name='building-confidence-list'),
    path('build-confidence/', BuildingConfidenceListView.as_view(), name='build-confidence-list-alias'),
    path('building-confidence/start-small/', StartSmallAudioView.as_view(), name='conf-start-small'),
    path('building-confidence/prepare-before-conversations/', PrepareBeforeConversationsAudioView.as_view(), name='conf-prepare-before-conversations'),
    path('building-confidence/be-patient-with-yourself/', BePatientWithYourselfAudioView.as_view(), name='conf-be-patient-with-yourself'),
    path('building-confidence/practice-every-day/', PracticeEveryDayAudioView.as_view(), name='conf-practice-every-day'),
    path('building-confidence/celebrate-progress/', CelebrateProgressAudioView.as_view(), name='conf-celebrate-progress'),

    # ========================================================
    # 4. Practice and Progress
    # ========================================================
    path('practice-and-progress/', PracticeAndProgressView.as_view(), name='practice-and-progress'),

    # Direct top-level aliases
    path('start-the-conversation/', StartConversationAudioView.as_view(), name='start-the-conversation'),
    path('start-the-converstion/', StartConversationAudioView.as_view(), name='start-the-converstion-alias'),
    path('manage-group-conversations/', ManageGroupConversationsAudioView.as_view(), name='manage-group-conversations'),
    path('improve-understanding/', ImproveUnderstandingAudioView.as_view(), name='improve-understanding'),
    path('handle-misunderstandings/', HandleMisunderstandingsAudioView.as_view(), name='handle-misunderstandings'),
    path('build-stronger-connections/', BuildStrongerConnectionsAudioView.as_view(), name='build-stronger-connections'),
    path('reduce-background-noise/', ReduceBackgroundNoiseAudioView.as_view(), name='direct-reduce-background-noise'),
    path('face-the-speaker/', FaceTheSpeakerAudioView.as_view(), name='direct-face-the-speaker'),
    path('take-breaks/', TakeBreaksAudioView.as_view(), name='direct-take-breaks'),
    path('use-visual-cues/', UseVisualCuesAudioView.as_view(), name='direct-use-visual-cues'),
    path('ask-for-repetition/', AskForRepetitionAudioView.as_view(), name='direct-ask-for-repetition'),

    # Generic lookup
    path('audio/<str:lookup>/', EverydayListeningTipDetailView.as_view(), name='audio-detail'),
    path('everyday-listening-tips/<str:lookup>/', EverydayListeningTipDetailView.as_view(), name='tip-detail'),
]