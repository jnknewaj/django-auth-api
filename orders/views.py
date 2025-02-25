from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer


class OrderViewSet(viewsets.ModelViewSet):
    # queryset = Order.objects.all().order_by("-order_date")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "seller":
            queryset = Order.objects.all().order_by("-order_date")
            customer_id = self.request.query_params.get("customer_id")
            if customer_id:
                queryset = queryset.filter(customer_id=customer_id)
            return queryset
        return Order.objects.filter(customer=user).order_by("-order_date")

    # serializer.save() normally just saves the data from the request.
    # Here, we override it to forcefully set the customer field to the logged-in user (self.request.user).
    # This ensures that a user cannot create an order for someone else.
    #
    # The perform_create() method is called when saving an object, and it is called by the create() method of the view.
    # @overriden
    # def perform_create(self, serializer):
    #     if self.request.user.role != "customer":
    #         return Response(
    #             {"detail": "Only customers can place orders."},
    #             status=status.HTTP_403_FORBIDDEN,
    #         )
    #     serializer.save(customer=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.role != "customer":
            raise serializers.ValidationError("Only customers can place orders.")
        serializer.save(customer=self.request.user)
        print("Order saved successfully 🚀")  # 🔥 Checkpoint


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
