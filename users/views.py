from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth import get_user_model # Move get_user_model here

# Create your views here.
"""
API Views for user authentication and profile management
All views return standardized response format
"""

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .authentication import FirebaseAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import get_user_model
#from progress.utils import mark_user_login
from django.utils import timezone
from django.conf import settings
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    FirebaseAuthSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetOTPVerifySerializer,
    ResendOTPSerializer,
    VerifyOTPSerializer,
    PasswordChangeSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    AccountDeleteSerializer,
    UserOnboardingSerializer,
    DailyCheckInSerializer,
    CheckInTutorialSerializer,
    CheckInTutorialFeedbackSerializer,
)
from django.db import IntegrityError
from .utils import (
    verify_firebase_token,
    send_welcome_email,
    send_account_deletion_email,
    get_client_ip,
    get_user_agent,
)
from .models import UserLoginHistory, AccountDeletionRequest, ProfileDataDeletionRequest, UserOnboarding, DailyCheckIn, CheckInTutorial, CheckInTutorialFeedback
from django.shortcuts import render

@csrf_exempt
def delete_profile_data_request_view(request):
    return render(request, 'users/delete_profile_data_request.html')

@method_decorator(csrf_exempt, name='dispatch')
class ProfileDataDeletionAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return render(request, 'users/delete_profile_data_request.html', {'error': 'Email is required.'})

        user = User.objects.filter(email=email).first()
        if user:
            deletion_request, created = ProfileDataDeletionRequest.objects.get_or_create(user=user, defaults={'email': email})
            
            verification_link = request.build_absolute_uri(
                reverse('users:verify_profile_data_deletion', kwargs={'token': str(deletion_request.verification_token)})
            )
            
            send_mail(
                'Verify Profile Data Deletion Request',
                f'Click the following link to delete your profile data: {verification_link}',
                'from@example.com',
                [email],
                fail_silently=False,
            )
        return render(request, 'users/delete_profile_data_submitted.html')

class VerifyProfileDataDeletionView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, token):
        try:
            deletion_request = ProfileDataDeletionRequest.objects.get(verification_token=token, status='pending')
            if deletion_request.user:
                user = deletion_request.user
                user.name = "User"
                user.date_of_birth = None
                user.gender = None
                user.occupation = None
                user.country = None
                user.bio = None
                if user.profile_picture:
                    user.profile_picture.delete(save=False)
                user.save()
                
                deletion_request.status = 'completed'
                deletion_request.save()
                return render(request, 'users/delete_profile_data_confirmed.html')
            else:
                deletion_request.status = 'completed'
                deletion_request.save()
                return render(request, 'users/delete_profile_data_confirmed.html')
        except ProfileDataDeletionRequest.DoesNotExist:
            return standard_response(success=False, message="Invalid or expired verification link.", status_code=status.HTTP_400_BAD_REQUEST)


User = get_user_model()

@csrf_exempt
def account_deletion_request_view(request):
    return render(request, 'users/delete_account.html')
@method_decorator(csrf_exempt, name='dispatch')
class AccountDeletionAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')

        if not name or not email:
            return render(request, 'users/delete_account.html', {'error': 'Name and email are required.'})

        user = User.objects.filter(email=email).first()
        if user:
            deletion_request, created = AccountDeletionRequest.objects.get_or_create(user=user, defaults={'name': name, 'email': email})

            # Create a verification link
            verification_link = request.build_absolute_uri(
                reverse('users:verify_account_deletion', kwargs={'token': str(deletion_request.verification_token)})
            )

            # Send email to the user
            send_mail(
                'Verify Account Deletion Request',
                f'Click the following link to delete your account: {verification_link}',
                'from@example.com',  # Replace with your sending email
                [email],
                fail_silently=False,
            )
        return render(request, 'users/deletion_request_submitted.html')


class VerifyAccountDeletionView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, token):
        try:
            deletion_request = AccountDeletionRequest.objects.get(verification_token=token, status='pending')
            if deletion_request.user:
                deletion_request.user.delete()
                deletion_request.user = None
                deletion_request.status = 'completed'
                deletion_request.save()
                return render(request, 'users/deletion_confirmed.html')
            else:
                # Handle case where user is not found, but request exists
                deletion_request.status = 'completed'
                deletion_request.save()
                return render(request, 'users/deletion_confirmed.html')
        except AccountDeletionRequest.DoesNotExist:
            return standard_response(success=False, message="Invalid or expired verification link.", status_code=status.HTTP_400_BAD_REQUEST)



def standard_response(success=True, message="", data=None, errors=None, status_code=status.HTTP_200_OK):
    """
    Create standardized API response
    
    Args:
        success (bool): Whether operation was successful
        message (str): Response message
        data (dict): Response data
        errors (dict): Error details (for failed operations)
        status_code (int): HTTP status code
        
    Returns:
        Response: DRF Response object with standardized format
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


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    """
    API endpoint for user registration (signup)
    
    POST /api/users/signup/
    
    Request body:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
    """
    
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def post(self, request):
        """Handle user registration"""
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            return standard_response(
                success=True,
                message="Registration successful. Please check your email for the OTP to verify your account.",
                data={
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'name': user.name,
                        'is_email_verified': user.is_email_verified,
                    }
                },
                status_code=status.HTTP_201_CREATED
            )
        
        return standard_response(
            success=False,
            message="Registration failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    """
    API endpoint for user login
    
    POST /api/users/login/
    
    Request body:
    {
        "email": "john@example.com",
        "password": "SecurePass123!"
    }
    """
    
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    
    def post(self, request):
        """Handle user login"""
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Log login history
            UserLoginHistory.objects.create(
                user=user,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                auth_method='email'
            )

            # Track daily login in progress app
            #mark_user_login(user)
            
            # Return success response with tokens
            return standard_response(
                success=True,
                message="Login successful",
                data={
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'name': user.name,
                        'is_email_verified': user.is_email_verified,
                        'profile_picture': user.profile_picture.url if user.profile_picture else None, # noqa
                    },
                    'tokens': {
                        'access': access_token,
                        'refresh': refresh_token,
                    }
                },
                status_code=status.HTTP_200_OK
            )
        
        # Return validation errors
        return standard_response(
            success=False,
            message="Login failed",
            errors=serializer.errors,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]
    """
    API endpoint for user logout
    
    POST /api/users/logout/
    
    Request body:
    {
        "refresh": "refresh_token_here"
    }
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Handle user logout by blacklisting refresh token"""
        try:
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return standard_response(
                    success=False,
                    message="Refresh token is required",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            if hasattr(token, 'blacklist'):
                token.blacklist()
            
            return standard_response(
                success=True,
                message="Logout successful",
                status_code=status.HTTP_200_OK
            )
        
        except TokenError:
            return standard_response(
                success=False,
                message="Invalid or expired token",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return standard_response(
                success=False,
                message=f"Logout failed: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )


import logging

logger = logging.getLogger(__name__)

class FirebaseAuthView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    """
    API endpoint for Firebase authentication (Google/Apple login)
    
    POST /api/users/firebase-auth/
    
    Request body:
    {
        "firebase_token": "firebase_id_token_from_client",
        "name": "John Doe" (optional),
        "date_of_birth": "1990-01-15" (optional)
    }
    """
    
    permission_classes = [AllowAny]
    serializer_class = FirebaseAuthSerializer
    
    def post(self, request):
        """Authenticate user with Firebase token"""
        logger.info(f"FirebaseAuthView POST request received. Headers: {request.headers}")
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            try:
                # Verify Firebase token
                firebase_token = serializer.validated_data['firebase_token']
                logger.info(f"Verifying Firebase token: {firebase_token[:30]}...")
                decoded_token = verify_firebase_token(firebase_token)
                logger.info(f"Firebase token verified successfully. Decoded token: {decoded_token}")
                
                # Extract user data from token or request
                firebase_uid = decoded_token.get('uid')
                email = decoded_token.get('email') or serializer.validated_data.get('email')
                if not email:
                    email = f"{firebase_uid}@privaterelay.appleid.com"
                
                raw_name = serializer.validated_data.get('name') or decoded_token.get('name')
                name = raw_name if raw_name else email.split('@')[0]
                
                # Determine auth provider
                firebase_provider = decoded_token.get('firebase', {}).get('sign_in_provider', 'google')
                auth_provider_map = {
                    'google.com': 'google',
                    'apple.com': 'apple',
                }
                auth_provider = auth_provider_map.get(firebase_provider, 'google')
                
                # Create or get user
                user = User.objects.create_firebase_user(
                    email=email,
                    name=name,
                    firebase_uid=firebase_uid,
                    auth_provider=auth_provider
                )
                
                # Update date of birth if provided
                dob = serializer.validated_data.get('date_of_birth')
                if dob and not user.date_of_birth:
                    user.date_of_birth = dob
                    user.save(update_fields=['date_of_birth'])
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                
                # Update last login
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                
                # Log login history
                UserLoginHistory.objects.create(
                    user=user,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    auth_method=auth_provider
                )

                # Mark user login in DailyProgress
                #mark_user_login(user)
                
                # Return success response
                return standard_response(
                    success=True,
                    message="Authentication successful",
                    data={
                        'user': {
                            'id': str(user.id),
                            'email': user.email,
                            'name': user.name,
                            'is_email_verified': user.is_email_verified,
                            'auth_provider': user.auth_provider,
                            'profile_picture': user.profile_picture.url if user.profile_picture else None,
                        },
                        'tokens': {
                            'access': access_token,
                            'refresh': refresh_token,
                        }
                    },
                    status_code=status.HTTP_200_OK
                )
            
            except Exception as e:
                logger.error(f"Firebase authentication failed: {str(e)}", exc_info=True)
                return standard_response(
                    success=False,
                    message=f"Firebase authentication failed: {str(e)}",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        logger.error(f"FirebaseAuthView serializer errors: {serializer.errors}")
        return standard_response(
            success=False,
            message="Invalid request data",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
"""
API Views - Part 2: Email Verification, Password Management, Profile
"""


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    """
    API endpoint to verify OTP
    """
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            try:
                user = User.objects.get(email=email)
                if user.otp == otp and user.is_otp_valid():
                    user.is_active = True
                    user.is_email_verified = True
                    user.clear_otp()
                    user.save()
                    return standard_response(success=True, message="OTP verified successfully.")
                else:
                    return standard_response(success=False, message="Invalid or expired OTP.", status_code=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return standard_response(success=False, message="User not found.", status_code=status.HTTP_404_NOT_FOUND)
        return standard_response(success=False, message="Invalid data.", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    """
    API endpoint to resend OTP
    """
    permission_classes = [AllowAny]
    serializer_class = ResendOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                if not user.is_active:
                    from .utils import generate_otp, send_otp_email
                    otp = generate_otp()
                    user.otp = otp
                    user.otp_created_at = timezone.now()
                    user.save(update_fields=['otp', 'otp_created_at'])
                    send_otp_email(user, otp)
                    return standard_response(success=True, message="OTP has been resent to your email.")
                else:
                    return standard_response(success=False, message="User is already active.", status_code=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return standard_response(success=False, message="User not found.", status_code=status.HTTP_404_NOT_FOUND)
        return standard_response(success=False, message="Invalid data.", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    """
    API endpoint to request password reset
    
    POST /api/users/password-reset/
    
    Request body:
    {
        "email": "john@example.com"
    }
    """
    
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer
    
    def post(self, request):
        """Request password reset"""
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Generate and send OTP
                from .utils import generate_otp, send_otp_email
                otp = generate_otp()
                user.otp = otp
                user.otp_created_at = timezone.now()
                user.save(update_fields=['otp', 'otp_created_at'])
                send_otp_email(user, otp)
            
            except User.DoesNotExist:
                # For security, don't reveal if email exists or not
                pass
            
            # Always return success message
            return standard_response(
                success=True,
                message="If an account with that email exists, an OTP has been sent.",
                status_code=status.HTTP_200_OK
            )
        
        return standard_response(
            success=False,
            message="Invalid request data",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetOTPVerifyView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    """
    API endpoint to verify OTP for password reset
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetOTPVerifySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            try:
                user = User.objects.get(email=email)
                if user.otp == otp and user.is_otp_valid():
                    # OTP is correct, allow password reset
                    user.clear_otp()
                    return standard_response(success=True, message="OTP verified successfully. You can now reset your password.")
                else:
                    return standard_response(success=False, message="Invalid or expired OTP.", status_code=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return standard_response(success=False, message="User not found.", status_code=status.HTTP_404_NOT_FOUND)
        return standard_response(success=False, message="Invalid data.", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    """
    API endpoint to confirm password reset with OTP
    
    POST /api/users/password-reset-confirm/
    
    Request body:
    {
        "email": "john@example.com",
        "password": "NewSecurePass123!",
        "confirm_password": "NewSecurePass123!"
    }
    """
    
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    
    def post(self, request):
        """Confirm password reset"""
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(email=email)
                
                # Set new password
                user.set_password(new_password)
                user.save()
                
                return standard_response(
                    success=True,
                    message="Password has been reset successfully. You can now login with your new password.",
                    status_code=status.HTTP_200_OK
                )
            
            except User.DoesNotExist:
                return standard_response(
                    success=False,
                    message="User not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
        
        return standard_response(
            success=False,
            message="Invalid request data",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    """
    API endpoint to change password (authenticated user)
    
    POST /api/users/password-change/
    
    Request body:
    {
        "old_password": "OldPass123!",
        "new_password": "NewSecurePass123!",
        "confirm_password": "NewSecurePass123!"
    }
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer
    
    def post(self, request):
        """Change password for authenticated user"""
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            # Verify old password
            if not user.check_password(old_password):
                return standard_response(
                    success=False,
                    message="Current password is incorrect",
                    errors={'old_password': ['Current password is incorrect']},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            return standard_response(
                success=True,
                message="Password changed successfully",
                status_code=status.HTTP_200_OK
            )
        
        return standard_response(
            success=False,
            message="Invalid request data",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]
    """
    API endpoint to get and update user profile
    
    GET /api/users/profile/ - Get user profile
    PUT /api/users/profile/ - Update full profile
    PATCH /api/users/profile/ - Partial update profile
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user profile"""
        user = request.user
        serializer = UserProfileSerializer(user)
        
        return standard_response(
            success=True,
            message="Profile retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    def put(self, request):
        """Update full user profile"""
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            
            # Return updated profile
            profile_serializer = UserProfileSerializer(user)
            
            return standard_response(
                success=True,
                message="Profile updated successfully",
                data=profile_serializer.data,
                status_code=status.HTTP_200_OK
            )
        
        return standard_response(
            success=False,
            message="Profile update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def patch(self, request):
        """Partial update user profile"""
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            # Return updated profile
            profile_serializer = UserProfileSerializer(user)
            
            return standard_response(
                success=True,
                message="Profile updated successfully",
                data=profile_serializer.data,
                status_code=status.HTTP_200_OK
            )
        
        return standard_response(
            success=False,
            message="Profile update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class AccountDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    """
    API endpoint to delete user account
    
    DELETE /api/users/account-delete/
    
    Request body:
    {
        "password": "user_password",
        "confirm_deletion": true
    }
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = AccountDeleteSerializer
    
    def delete(self, request):
        """Delete user account"""
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            password = serializer.validated_data['password']
            
            # Verify password (for email/password users)
            if user.auth_provider == 'email':
                if not user.check_password(password):
                    return standard_response(
                        success=False,
                        message="Incorrect password",
                        errors={'password': ['Incorrect password']},
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            
            # Store email for confirmation email
            user_email = user.email
            user_name = user.name
            
            # Send account deletion confirmation email before deleting
            try:
                send_account_deletion_email(user)
            except Exception:
                pass  # Continue with deletion even if email fails
            
            # Delete user account
            user.delete()
            
            return standard_response(
                success=True,
                message="Account deleted successfully",
                status_code=status.HTTP_200_OK
            )
        
        return standard_response(
            success=False,
            message="Account deletion failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view with standard response format
    
    POST /api/users/token/refresh/
    
    Request body:
    {
        "refresh": "refresh_token_here"
    }
    """
    
    def post(self, request, *args, **kwargs):
        """Refresh access token"""
        try:
            response = super().post(request, *args, **kwargs)
            
            return standard_response(
                success=True,
                message="Token refreshed successfully",
                data=response.data,
                status_code=status.HTTP_200_OK
            )
        
        except TokenError as e:
            return standard_response(
                success=False,
                message="Token refresh failed",
                errors={'detail': str(e)},
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except InvalidToken as e:
            return standard_response(
                success=False,
                message="Invalid token",
                errors={'detail': str(e)},
                status_code=status.HTTP_401_UNAUTHORIZED
            )


class CustomTokenVerifyView(TokenVerifyView):
    """
    Custom token verify view with standard response format
    
    POST /api/users/token/verify/
    
    Request body:
    {
        "token": "access_token_here"
    }
    """
    
    def post(self, request, *args, **kwargs):
        """Verify access token"""
        try:
            response = super().post(request, *args, **kwargs)
            
            return standard_response(
                success=True,
                message="Token is valid",
                data={'valid': True},
                status_code=status.HTTP_200_OK
            )
        
        except TokenError as e:
            return standard_response(
                success=False,
                message="Token is invalid or expired",
                data={'valid': False},
                errors={'detail': str(e)},
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except InvalidToken as e:
            return standard_response(
                success=False,
                message="Invalid token",
                data={'valid': False},
                errors={'detail': str(e)},
                status_code=status.HTTP_401_UNAUTHORIZED
            )


class OnboardingView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]
    serializer_class = UserOnboardingSerializer
    """
    API endpoint for User Onboarding
    
    GET /api/users/onboarding/ - Get onboarding responses and status
    POST /api/users/onboarding/ - Submit onboarding responses
    """

    def get(self, request):
        """Get user onboarding data"""
        try:
            onboarding = request.user.onboarding
            serializer = self.serializer_class(onboarding)
            return standard_response(
                success=True,
                message="Onboarding data retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except UserOnboarding.DoesNotExist:
            return standard_response(
                success=True,
                message="Onboarding not yet completed",
                data={'is_completed': False},
                status_code=status.HTTP_200_OK
            )

    def post(self, request):
        """Submit or update user onboarding data"""
        user = request.user
        onboarding_instance = getattr(user, 'onboarding', None)
        serializer = self.serializer_class(onboarding_instance, data=request.data)

        if serializer.is_valid():
            serializer.save(user=user, is_completed=True)
            return standard_response(
                success=True,
                message="Onboarding responses saved successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK if onboarding_instance else status.HTTP_201_CREATED
            )

        return standard_response(
            success=False,
            message="Onboarding submission failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class OnboardingOptionsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    """
    API endpoint to fetch available question options for the onboarding questionnaire
    
    GET /api/users/onboarding/options/
    """

    def get(self, request):
        hearing_journey_options = [
            {"value": key, "label": label}
            for key, label in UserOnboarding.HEARING_JOURNEY_CHOICES
        ]
        improvement_goals_options = [
            {"value": key, "label": label}
            for key, label in UserOnboarding.IMPROVEMENT_GOALS_CHOICES
        ]

        return standard_response(
            success=True,
            message="Onboarding options retrieved successfully",
            data={
                "question_1": {
                    "title": "Where are you in your hearing journey?",
                    "type": "single_choice",
                    "options": hearing_journey_options
                },
                "question_2": {
                    "title": "What do you most want to improve?",
                    "type": "multiple_choice",
                    "required_selection_count": 3,
                    "options": improvement_goals_options
                }
            },
            status_code=status.HTTP_200_OK
        )


class DailyCheckInView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]
    serializer_class = DailyCheckInSerializer
    """
    API endpoint for Daily Check-in ("How are you hearing today?")
    
    GET /api/users/checkin/ - Get today's check-in status and history
    POST /api/users/checkin/ - Submit or update today's check-in
    PATCH /api/users/checkin/ - Partial update today's check-in (e.g. adding 'what_went_well')
    """

    def get(self, request):
        """Get user check-in status for today and recent history"""
        user = request.user
        today = timezone.now().date()

        today_checkin = DailyCheckIn.objects.filter(user=user, checkin_date=today).first()
        recent_checkins = DailyCheckIn.objects.filter(user=user)[:30]

        serializer = self.serializer_class(today_checkin) if today_checkin else None
        history_serializer = self.serializer_class(recent_checkins, many=True)

        return standard_response(
            success=True,
            message="Check-in status retrieved successfully",
            data={
                "has_checked_in_today": today_checkin is not None,
                "today_checkin": serializer.data if serializer else None,
                "recent_history": history_serializer.data
            },
            status_code=status.HTTP_200_OK
        )

    def post(self, request):
        """Submit or update today's daily check-in"""
        user = request.user
        today = timezone.now().date()

        existing_checkin = DailyCheckIn.objects.filter(user=user, checkin_date=today).first()
        serializer = self.serializer_class(existing_checkin, data=request.data, partial=True) if existing_checkin else self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                checkin = serializer.save(user=user, checkin_date=today)
                is_update = existing_checkin is not None
                return standard_response(
                    success=True,
                    message="Daily check-in updated successfully." if is_update else "Daily check-in submitted successfully.",
                    data=self.serializer_class(checkin).data,
                    status_code=status.HTTP_200_OK if is_update else status.HTTP_201_CREATED
                )
            except IntegrityError:
                return standard_response(
                    success=False,
                    message="An error occurred while saving your daily check-in.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        return standard_response(
            success=False,
            message="Check-in submission failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request):
        """Update today's check-in details (e.g. what_went_well)"""
        user = request.user
        today = timezone.now().date()

        today_checkin = DailyCheckIn.objects.filter(user=user, checkin_date=today).first()
        if not today_checkin:
            return standard_response(
                success=False,
                message="No check-in found for today. Please start your daily check-in first.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(today_checkin, data=request.data, partial=True)
        if serializer.is_valid():
            checkin = serializer.save()
            return standard_response(
                success=True,
                message="Daily check-in updated successfully.",
                data=self.serializer_class(checkin).data,
                status_code=status.HTTP_200_OK
            )

        return standard_response(
            success=False,
            message="Check-in update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class DailyCheckInOptionsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    """
    API endpoint to fetch daily check-in question, available choices, and follow-up flows
    
    GET /api/users/checkin/options/
    """

    def get(self, request):
        options = [
            {
                "value": "good",
                "label": "Good",
                "followup": {
                    "has_followup": True,
                    "prompt": "What went well today?",
                    "field_name": "what_went_well",
                    "input_type": "text"
                }
            },
            {
                "value": "okay",
                "label": "Okay",
                "followup": {
                    "has_followup": True,
                    "prompt": "What went okay today?",
                    "field_name": "what_went_okay",
                    "input_type": "text"
                }
            },
            {
                "value": "struggling",
                "label": "Struggling",
                "followup": {
                    "has_followup": True,
                    "prompt": "Tell us why you're struggling",
                    "field_name": "why_struggling",
                    "input_type": "text"
                }
            },
            {
                "value": "frustrated",
                "label": "Frustrated",
                "followup": {
                    "has_followup": True,
                    "prompt": "Tell us why you're struggling",
                    "field_name": "why_struggling",
                    "input_type": "text"
                }
            }
        ]
        return standard_response(
            success=True,
            message="Check-in options retrieved successfully",
            data={
                "question": "How are you hearing today?",
                "type": "single_choice",
                "options": options
            },
            status_code=status.HTTP_200_OK
        )


class CheckInTutorialListView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = CheckInTutorialSerializer
    """
    API endpoint to list active check-in tutorial videos and instructions
    
    GET /api/users/tutorials/
    GET /api/users/tutorials/?category=Sound Adjustment
    """

    def get(self, request):
        category = request.query_params.get('category')
        queryset = CheckInTutorial.objects.filter(is_active=True)
        if category:
            queryset = queryset.filter(category__iexact=category)

        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return standard_response(
            success=True,
            message="Check-in tutorials retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class CheckInTutorialDetailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = CheckInTutorialSerializer
    """
    API endpoint to retrieve single check-in tutorial by slug or ID
    
    GET /api/users/tutorials/<slug_or_id>/
    """

    def get(self, request, slug):
        if slug.isdigit():
            tutorial = CheckInTutorial.objects.filter(id=int(slug), is_active=True).first()
        else:
            tutorial = CheckInTutorial.objects.filter(slug=slug, is_active=True).first()

        if not tutorial:
            return standard_response(
                success=False,
                message="Tutorial not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(tutorial, context={'request': request})
        return standard_response(
            success=True,
            message="Tutorial details retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class CheckInTutorialFeedbackView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]
    serializer_class = CheckInTutorialFeedbackSerializer
    """
    API endpoint for submitting 'This still feels wrong' feedback on tutorials
    
    POST /api/users/checkin-tutorials/feedback/
    """

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            feedback = serializer.save(user=request.user)
            return standard_response(
                success=True,
                message="Feedback submitted successfully.",
                data=self.serializer_class(feedback).data,
                status_code=status.HTTP_201_CREATED
            )

        return standard_response(
            success=False,
            message="Feedback submission failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


from .models import HearingAidWearTime
from .serializers import HearingAidWearTimeSerializer, HearingAidWearTimeInputSerializer


def calculate_user_hearing_score(user):
    """
    Calculate a single objective Hearing Score number between 1 and 100 based on real user data:
    1. Wear Time Consistency (Max 40 Points): Target = 8+ hours/day of hearing machine usage.
    2. Daily Lesson Completion (Max 30 Points): Active participation in rehabilitation program.
    3. Daily Check-in Consistency (Max 20 Points): Sound comfort & symptom tracking.
    4. Strategy & Onboarding Engagement (Max 10 Points): Profile & listening habit setup.
    """
    today = timezone.now().date()
    fourteen_days_ago = today - timezone.timedelta(days=14)

    # 1. Wear Time Score (40 Points Max)
    wear_logs = HearingAidWearTime.objects.filter(user=user, date__gte=fourteen_days_ago)
    if wear_logs.exists():
        total_hours = sum([log.total_hours for log in wear_logs])
        avg_daily_hours = total_hours / max(wear_logs.count(), 1)
        wear_time_score = min(40.0, (avg_daily_hours / 8.0) * 40.0)
    else:
        wear_time_score = 0.0

    # 2. Daily Lesson Completion Score (30 Points Max)
    try:
        from learn.models import UserLessonProgress, DailyLesson
        progress = UserLessonProgress.objects.filter(user=user).first()
        total_lessons = DailyLesson.objects.filter(is_active=True).count() or 1
        if progress and progress.completed_days:
            completed_count = len(progress.completed_days)
            lesson_score = min(30.0, (completed_count / total_lessons) * 30.0)
        else:
            lesson_score = 0.0
    except Exception:
        lesson_score = 0.0

    # 3. Check-in Consistency Score (20 Points Max)
    checkin_count = DailyCheckIn.objects.filter(user=user, checkin_date__gte=fourteen_days_ago).count()
    checkin_score = min(20.0, (checkin_count / 7.0) * 20.0)

    # 4. Strategy & Onboarding Engagement Score (10 Points Max)
    has_onboarding = hasattr(user, 'onboarding') and user.onboarding.is_completed
    strategy_score = 10.0 if has_onboarding else 5.0

    # Total score integer strictly bounded between 1 and 100
    score = int(round(wear_time_score + lesson_score + checkin_score + strategy_score))
    return max(1, min(100, score))


class HearingAidWearTimeView(APIView):
    """
    API endpoint for logging and retrieving daily hearing machine wear time in hours and minutes
    
    GET /api/users/wear-time/ - Get wear time history and weekly/monthly averages
    POST /api/users/wear-time/ - Submit or update daily wear time
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        today = timezone.now().date()
        logs = HearingAidWearTime.objects.filter(user=request.user).order_by('-date', '-created_at')

        today_log = logs.filter(date=today).first()
        today_data = HearingAidWearTimeSerializer(today_log).data if today_log else None

        # Calculate weekly & monthly average wear hours
        seven_days_ago = today - timezone.timedelta(days=7)
        weekly_logs = logs.filter(date__gte=seven_days_ago)
        weekly_total_hours = sum([log.total_hours for log in weekly_logs])
        weekly_avg_hours = round(weekly_total_hours / max(weekly_logs.count(), 1), 2) if weekly_logs.exists() else 0.0

        thirty_days_ago = today - timezone.timedelta(days=30)
        monthly_logs = logs.filter(date__gte=thirty_days_ago)
        monthly_total_hours = sum([log.total_hours for log in monthly_logs])
        monthly_avg_hours = round(monthly_total_hours / max(monthly_logs.count(), 1), 2) if monthly_logs.exists() else 0.0

        history_serializer = HearingAidWearTimeSerializer(logs[:30], many=True)

        return standard_response(
            success=True,
            message="Wear time data retrieved successfully",
            data={
                "today_wear_time": today_data,
                "weekly_average_hours": weekly_avg_hours,
                "monthly_average_hours": monthly_avg_hours,
                "total_logged_days": logs.count(),
                "wear_time_history": history_serializer.data,
            },
            status_code=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = HearingAidWearTimeInputSerializer(data=request.data)
        if not serializer.is_valid():
            return standard_response(
                success=False,
                message="Validation failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        validated = serializer.validated_data
        log_date = validated.get('date') or timezone.now().date()

        wear_time_log, created = HearingAidWearTime.objects.update_or_create(
            user=request.user,
            date=log_date,
            defaults={
                'hours': validated['hours'],
                'minutes': validated['minutes'],
                'notes': validated.get('notes', ''),
            }
        )

        return standard_response(
            success=True,
            message="Wear time logged successfully",
            data=HearingAidWearTimeSerializer(wear_time_log).data,
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class HearingScoreView(APIView):
    """
    API endpoint to fetch user's single Hearing Score number (between 1 and 100)
    
    GET /api/users/hearing-score/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, FirebaseAuthentication]

    def get(self, request):
        hearing_score = calculate_user_hearing_score(request.user)
        return standard_response(
            success=True,
            message="Hearing score retrieved successfully",
            data={
                "hearing_score": hearing_score,
                "score": hearing_score
            },
            status_code=status.HTTP_200_OK
        )


