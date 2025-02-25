from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderItemViewSet

router = DefaultRouter()
# Handles /api/orders/
router.register(r"", OrderViewSet, basename="order")
# Handles /api/orders/items/
router.register(r"items", OrderItemViewSet, basename="orderitem")

urlpatterns = [
    path("", include(router.urls)),
]
