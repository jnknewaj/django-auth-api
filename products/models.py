from django.db import models
import uuid


class Product(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveBigIntegerField()
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# {
#     "name": "Kacchi Biriyani",
#     "description": "Kacchi Biriyani is a traditional dish in Bangladesh and Pakistan.",
#     "price": 200,
#     "stock": 100,
# }
