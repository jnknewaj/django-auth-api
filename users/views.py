from django.shortcuts import render
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    PasswordResetRequestSerialier,
    PasswordResetConfirmSerializer,
)
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import GenericAPIView

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model


User = get_user_model()
token_generator = PasswordResetTokenGenerator()

# Notes on `request` object in Django REST Framework (DRF):
# --------------------------------------------------------
# 1. request.data:
#    - Parsed request body data (e.g., JSON, form data).
#    - Example: {"email": "user@example.com", "password": "securepass123", "role": "customer"}

# 2. request.query_params:
#    - Query parameters from the URL (GET params).
#    - Example: /api/users/register/?ref=promo123
#    - Access: request.query_params.get('ref')

# 3. request.headers:
#    - HTTP headers (e.g., Authorization, Content-Type).
#    - Example: request.headers.get('Authorization')

# 4. request.user:
#    - The currently authenticated user, or AnonymousUser if not authenticated.

# 5. request.method:
#    - HTTP method used in the request (GET, POST, PUT, DELETE, etc.).
#    - Example: request.method == "POST"


# 6. request.FILES:
#    - Handles uploaded files when Content-Type is multipart/form-data.
#    - Example: request.FILES.get('profile_picture')
class UserRegistrationView(APIView):

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = self.get_tokens_for_user(user)
            return Response(
                {
                    "message": "User registered successfully.",
                    "tokens": tokens,
                    "user": {
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.role,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogOutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            raise ValidationError({"refresh": "Refresh token is required for logout."})

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logout successful."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):

    def post(self, request):
        serializer = PasswordResetRequestSerialier(data=request.data)
        if serializer.is_valid():
            # not raising DoesNotExist error for security purpose
            user = User.objects.get(email=serializer.validated_data["email"])
            token = token_generator.make_token(user)
            # Converts the relative URL into an absolute one,
            # including the domain (e.g., http://127.0.0.1:8000/...).
            reset_link = request.build_absolute_uri(
                # Generates a relative URL for the password reset confirmation view using
                # the user’s primary key and the token as arguments.
                reverse("password-reset-confirm", args=[user.pk, token])  # explain
            )
            send_mail(
                "Password Reset Request",  # subject
                f"Click the link to reset your password: {reset_link}",  # body
                settings.DEFAULT_FROM_EMAIL,  # from
                [user.email],  # to
                fail_silently=False,  # if error occurs will raise exception
            )
            return Response(
                {"message": "Password reset link sent."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class PasswordResetConfirmView(APIView):
#     # serializer_class = PasswordResetConfirmSerializer

#     def post(self, request, uid, token):
#         try:
#             # Fetch user by ID from URL.
#             # The pk alias always refers to the field marked as primary_key=True
#             # it can also be written as : user = User.objects.get(id=uid)
#             user = User.objects.get(pk=uid)
#         except User.DoesNotExist:
#             return Response(
#                 {"error": "Invalid user ID."}, status=status.HTTP_400_BAD_REQUEST
#             )

#         if not token_generator.check_token(user, token):
#             return Response(
#                 {"error": "Invalid or expired token."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         serializer = PasswordResetConfirmSerializer(data=request.data)
#         # serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             user.set_password(serializer.validated_data["new_password"])
#             user.save()
#             return Response(
#                 {"message": "Password reset successful."}, status=status.HTTP_200_OK
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uid, token):
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid user ID."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(
            data=request.data
        )  # ✅ Simpler with GenericAPIView
        if serializer.is_valid():
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(
                {"message": "Password reset successful."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
