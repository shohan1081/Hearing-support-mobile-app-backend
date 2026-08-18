from django.urls import path
from .views import (
    EverydayListeningTipListView,
    EverydayListeningTipDetailView,
)

app_name = 'skills_strategies'

urlpatterns = [
    # Everyday Listening Tips Audio APIs
    path('everyday-listening-tips/', EverydayListeningTipListView.as_view(), name='tip-list'),
    path('everyday-listening-tips/<str:lookup>/', EverydayListeningTipDetailView.as_view(), name='tip-detail'),
]
