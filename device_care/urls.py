from django.urls import path
from .views import (
    HearingAidBrandListView,
    HearingAidBrandDetailView,
    HearingAidModelListView,
    HearingAidModelDetailView,
    DeviceCareSectionDetailView,
)

app_name = 'device_care'

urlpatterns = [
    # Brands APIs
    path('brands/', HearingAidBrandListView.as_view(), name='brand-list'),
    path('brands/<str:lookup>/', HearingAidBrandDetailView.as_view(), name='brand-detail'),

    # Models APIs
    path('models/', HearingAidModelListView.as_view(), name='model-list'),
    path('models/<str:lookup>/', HearingAidModelDetailView.as_view(), name='model-detail'),

    # Section Detail API
    path('sections/<int:pk>/', DeviceCareSectionDetailView.as_view(), name='section-detail'),
]
