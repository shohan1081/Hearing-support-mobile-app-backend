from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.authentication import FirebaseAuthentication

from .models import HearingAidBrand, HearingAidModel, DeviceCareSection
from .serializers import (
    HearingAidBrandListSerializer,
    HearingAidBrandDetailSerializer,
    HearingAidModelListSerializer,
    HearingAidModelDetailSerializer,
    DeviceCareSectionSerializer,
)
from .utils import seed_default_device_care_data


def standard_response(success=True, message="", data=None, errors=None, status_code=status.HTTP_200_OK):
    """
    Create standardized API response for consistency across the application
    """
    response_data = {
        'success': success,
        'message': message,
    }
    if data is not None:
        response_data['data'] = data
    if errors is not None:
        response_data['errors'] = errors
    return Response(response_data, status=status_code)


class HearingAidBrandListView(APIView):
    """
    API endpoint to list all hearing aid brands (Phonak, Oticon, ReSound, Widex, Starkey, etc.)
    
    GET /api/device-care/brands/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_device_care_data()
        brands = HearingAidBrand.objects.filter(is_active=True).order_by('order', 'name')
        serializer = HearingAidBrandListSerializer(brands, many=True, context={'request': request})
        return standard_response(
            success=True,
            message="Hearing aid brands retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class HearingAidBrandDetailView(APIView):
    """
    API endpoint to get brand details & list of device models under that brand
    
    GET /api/device-care/brands/<slug_or_id>/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request, lookup):
        seed_default_device_care_data()
        brand = None

        if lookup.isdigit():
            brand = HearingAidBrand.objects.filter(pk=int(lookup), is_active=True).first()

        if not brand:
            brand = HearingAidBrand.objects.filter(slug=lookup, is_active=True).first()

        if not brand:
            return standard_response(
                success=False,
                message=f"Hearing aid brand '{lookup}' not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = HearingAidBrandDetailSerializer(brand, context={'request': request})
        return standard_response(
            success=True,
            message=f"Brand '{brand.name}' details retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class HearingAidModelListView(APIView):
    """
    API endpoint to list all hearing aid device models
    
    GET /api/device-care/models/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        seed_default_device_care_data()
        models = HearingAidModel.objects.filter(is_active=True).order_by('brand__order', 'order', 'name')
        serializer = HearingAidModelListSerializer(models, many=True, context={'request': request})
        return standard_response(
            success=True,
            message="Hearing aid models retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class HearingAidModelDetailView(APIView):
    """
    API endpoint to get complete device model details including all 4 care sections (cleaning guide, care tips, troubleshooting, user manual)
    
    GET /api/device-care/models/<slug_or_id>/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request, lookup):
        seed_default_device_care_data()
        model = None

        if lookup.isdigit():
            model = HearingAidModel.objects.filter(pk=int(lookup), is_active=True).first()

        if not model:
            model = HearingAidModel.objects.filter(slug=lookup, is_active=True).first()

        if not model:
            return standard_response(
                success=False,
                message=f"Hearing aid model '{lookup}' not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = HearingAidModelDetailSerializer(model, context={'request': request})
        return standard_response(
            success=True,
            message=f"Model '{model.name}' care details retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class DeviceCareSectionDetailView(APIView):
    """
    API endpoint to get detail view for a specific care section by ID
    
    GET /api/device-care/sections/<pk>/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request, pk):
        seed_default_device_care_data()
        try:
            section = DeviceCareSection.objects.get(pk=pk, is_active=True)
        except DeviceCareSection.DoesNotExist:
            return standard_response(
                success=False,
                message="Device care section not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = DeviceCareSectionSerializer(section, context={'request': request})
        return standard_response(
            success=True,
            message=f"Section '{section.title}' details retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
