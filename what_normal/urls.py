from django.urls import path
from .views import (
    WhatNormalVideoListView,
    WhatNormalVideoDetailView,
    WhatNormalAudioListView,
    WhatNormalAudioDetailView,
)

app_name = 'what_normal'

urlpatterns = [
    # Video APIs
    path('videos/', WhatNormalVideoListView.as_view(), name='video-list'),
    path('videos/<int:pk>/', WhatNormalVideoDetailView.as_view(), name='video-detail'),

    # Audio APIs
    path('audios/', WhatNormalAudioListView.as_view(), name='audio-list'),
    path('audios/<int:pk>/', WhatNormalAudioDetailView.as_view(), name='audio-detail'),
]
