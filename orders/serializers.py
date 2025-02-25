from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer
from products.models import Product
import logging

logger = logging.getLogger(__name__)


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )  # Allow adding product via ID

    class Meta:
        model = OrderItem
        # will create 400 bad req if we dont exclude order
        exclude = [
            "order"
        ]  # 💥 Exclude 'order' field as it will be set by OrderSerializer


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    items = OrderItemSerializer(many=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = "__all__"

    def create(self, validated_data):
        logger.info(f"Validated data received: {validated_data}")  # 🔥 Debug line
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        logger.info(f"Order created: {order}")  # 🔥 Debug line

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            logger.info(f"OrderItem created with data: {item_data}")  # 🔥 Debug line

        return order
