from rest_framework import viewsets, permissions, decorators, response, status
from ..serializers import UserProfileSerializer


class UserProfileView(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.__class__.objects.filter(pk=self.request.user.pk)

    # @action decorator: Adds custom endpoints to a ViewSet.
    # detail=False:
    #   If True, the endpoint expects a user ID (/profile/1/).
    #   If False (here), it doesn’t expect an ID (/profile/me/).
    # methods=["get", "put"]:
    #   We’re allowing both GET (to fetch profile) and PUT (to update profile) requests.
    # url_path="me":
    #   This means the endpoint will be accessible at /profile/me/
    @decorators.action(detail=False, methods=["get", "put"], url_path="me")
    def me(self, request):
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return response.Response(serializer.data)

        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)
