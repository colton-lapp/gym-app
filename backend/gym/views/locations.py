# views/locations.py
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import UserLocation, GymSession
from ..serializers.locations import UserLocationSerializer
from ..serializers.sessions import  GymSessionSerializer

class UserLocationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserLocationSerializer
    permission_classes = [IsAuthenticated]
    queryset = UserLocation.objects.all() 

    def get_queryset(self):
        return UserLocation.objects.for_user(self.request.user).recent_first()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def most_recent(self, request):
        loc = self.get_queryset().first()
        if not loc:
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(loc)
        return Response(serializer.data)