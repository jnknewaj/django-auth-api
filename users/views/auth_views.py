from ..serializers import (
    UserRegistrationSerializer,
)
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


class UserRegistrationView(APIView):

    def send_verification_email(self, user, request):
        token = token_generator.make_token(user)
        verification_link = request.build_absolute_uri(
            reverse("email-verify", kwargs={"uid": user.pk, "token": token})
        )
        send_mail(
            subject="Verify your email",
            message=f"Click the link to verify your email: {verification_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

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
            self.send_verification_email(user, request)
            return Response(
                {
                    "message": "User registered successfully. Check your email to verify your account.",
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


class EmailVerifyView(APIView):
    def get(self, request, uid, token):
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid user ID."}, status=status.HTTP_400_BAD_REQUEST
            )

        if token_generator.check_token(user, token):
            user.is_email_verified = True
            user.save()
            return Response(
                {"message": "Email verified successfully!"}, status=status.HTTP_200_OK
            )
        return Response(
            {"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST
        )


# Accept the user's email via a POST request.
# Check if the user exists.
# If the user exists and is not already verified, generate a new token and send the verification email again.
class ResendVerificationView(APIView):

    def post(self, request):
        email = request.data.get("email")
        if not email:
            raise ValidationError({"email": "Email is required."})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_email_verified:
            return Response(
                {"message": "Account is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate a new token
        token = token_generator.make_token(user)
        verification_link = request.build_absolute_uri(
            reverse("email-verify", kwargs={"uid": user.pk, "token": token})
        )

        # Send the verification email
        send_mail(
            subject="Verify your email",
            message=f"Click the link to verify your email: {verification_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {"message": "Verification email sent."},
            status=status.HTTP_200_OK,
        )
