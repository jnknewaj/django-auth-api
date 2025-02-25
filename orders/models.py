from django.db import models
from users.models import User
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
    ]

    order_id = models.AutoField(primary_key=True, editable=False)
    # user.orders.all() will return all the Order objects related to the User object
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    order_date = models.DateTimeField(auto_now_add=True)
    shipping_address = models.TextField()

    # @property is a decorator that allows you to access the total_price() as an instance method
    @property
    def total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())

    def __str__(self):
        return f"Order {self.order_id} - {self.status}"


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    # order.items.all() will return all the OrderItem objects related to the Order object
    # related_name is used to access the OrderItem objects from the Order object
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
