from django.urls import path
from .views import (
    UserRegistrationView,
    LogOutView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# api/users/...
urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogOutView.as_view(), name="user_logout"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path(
        "password-reset-confirm/<uid>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]


"""
Client Request
     |
     v
URL Configuration (urls.py)
     |
     v
View (views.py)
     |
     v
Serializer (serializers.py)
     |
     v
Model (models.py)
     |
     v
Database
"""
