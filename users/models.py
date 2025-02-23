from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin

USER_ROLE_CHOICES = (("customer", "Customer"), ("seller", "Seller"))


# When calling `User.objects.create_user(email, password, role)`,
# Django uses the create_user method() from CustomUserManager
# -- User can register even without a password
class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, role="customer", **extra_fields):
        print("CustomUserManager.create_user called")
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        # here self.model refers to the User model
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, "seller", **extra_fields)


class User(AbstractUser, PermissionsMixin):

    # we don't need username field, but django by default adds one, so removing
    username = None
    # In Django, pk is a universal alias for the primary key of a model,
    # regardless of the field name.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(
        max_length=10, choices=USER_ROLE_CHOICES, default="customer"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_email_verified = models.BooleanField(default=False)  # added later

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role"]

    def __str__(self):
        return self.email


class Address(models.Model):

    ADDRESS_TYPES = (
        ("billing", "Billing"),
        ("shipping", "Shipping"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address_type = models.CharField(
        max_length=10, choices=ADDRESS_TYPES, default="shipping"
    )
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    street_address = models.TextField()
    zip_code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.address_type}"
