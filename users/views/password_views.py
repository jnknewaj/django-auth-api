from ..serializers import (
    PasswordResetRequestSerialier,
    PasswordResetConfirmSerializer,
)
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model

User = get_user_model()
token_generator = PasswordResetTokenGenerator()

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
