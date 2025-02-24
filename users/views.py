# Notes on `request` object in Django REST Framework (DRF):
# --------------------------------------------------------
# 1. request.data:
#    - Parsed request body data (e.g., JSON, form data).
#    - Example: {"email": "user@example.com", "password": "securepass123", "role": "customer"}

# 2. request.query_params:
#    - Query parameters from the URL (GET params).
#    - Example: /api/users/register/?ref=promo123
#    - Access: request.query_params.get('ref')

# 3. request.headers:
#    - HTTP headers (e.g., Authorization, Content-Type).
#    - Example: request.headers.get('Authorization')

# 4. request.user:
#    - The currently authenticated user, or AnonymousUser if not authenticated.

# 5. request.method:
#    - HTTP method used in the request (GET, POST, PUT, DELETE, etc.).
#    - Example: request.method == "POST"


# 6. request.FILES:
#    - Handles uploaded files when Content-Type is multipart/form-data.
#    - Example: request.FILES.get('profile_picture')


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
