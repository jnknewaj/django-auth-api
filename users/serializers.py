from rest_framework import serializers
from .models import User, Address

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

# When you need to:
# 1. Validate and transform incoming data before it interacts with models or views.
# 2. Handle complex input data that needs to be validated (e.g., multiple fields or nested structures).
# 3. Perform advanced validation, such as checking the uniqueness of a field or enforcing custom rules.
# 4. Serialize model instances to transform data into a specific format (e.g., JSON).
# 5. Convert model instances (or querysets) to a format that can be returned in an API response.
# 6. Create, update, or delete objects in the database (e.g., creating or updating a User model).
# 7. Ensure that the input data conforms to the required format, such as checking if an email is valid or password matches.
# 8. Provide clear error messages in case of validation failures (e.g., invalid email, missing required fields).
# 9. Use serializers for pagination, filtering, and other features related to querying the database.
# 10. Need to define fields explicitly that will be included in the API response or expected in the request.
# 11. Allow reusability of the validation logic across multiple views or endpoints.
# 12. Handle file uploads or other binary data.
# 13. Support custom field types (e.g., custom validators, fields based on certain conditions).

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
            "date_joined",
        ]


# here we can override 'validate()' or 'validate_field_name()'
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone", "password"]
        extra_kwargs = {"password": {"write_only": True}}  # Hide password in response

    def create(self, validated_data):
        # option 1
        # user = User(
        #     email=validated_data("email"),
        #     first_name=validated_data("first_name"),
        #     last_name=validated_data("last_name"),
        #     phone = validated_data("phone"),
        # )
        # user.set_password(validated_data["password"])
        # user.save()
        # return user

        # option 2
        # password = validated_data.pop('password')
        # user = User(**validated_data)
        # user.set_password(password )
        # user.save()
        # return user

        # option 3
        user = User.objects.create_user(**validated_data)
        return user

    # this will prevent passing unexpected fields
    def to_internal_value(self, data):
        valid_fields = set(self.get_fields().keys())
        for field in data.keys():
            if field not in valid_fields:
                raise serializers.ValidationError({field: "This field is not valid."})
        return super().to_internal_value(data)


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for user addresses."""

    class Meta:
        model = Address
        fields = (
            "id",
            "user",
            "address_type",
            "country",
            "state",
            "city",
            "street_address",
            "zip_code",
        )
        read_only_fields = ("user",)  # user will be set from the request user

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    # {
    #     "email": "nij@example.com",
    #     "first_name": "Ni",
    #     "last_name": "Jh",
    #     "phone": "1234567890",
    #     "password": "password123",
    # }


class PasswordResetRequestSerialier(serializers.Serializer):
    # validates that the value provided is a valid email address.
    # If the input is not a valid email format, the serializer will automatically raise
    # a validation error.
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user associated with that email")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data
