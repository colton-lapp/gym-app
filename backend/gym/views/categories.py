from rest_framework import viewsets, permissions
from django.db import models
from ..models import MuscleGroup, Tag
from ..serializers.categories import MuscleGroupSerializer, TagSerializer


class MuscleGroupViewSet(viewsets.ModelViewSet):
    """
    Endpoints:
    - GET  /api/muscle-groups/
    - POST /api/muscle-groups/
    - PATCH /api/muscle-groups/{id}/
    - DELETE /api/muscle-groups/{id}/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MuscleGroupSerializer
    queryset = MuscleGroup.objects.all()

    def get_queryset(self):
        """
        Return:
        - User’s custom groups
        - Default groups (user=None)
        """
        user = self.request.user
        return MuscleGroup.objects.filter(
            models.Q(user=user) | models.Q(user__isnull=True)
        )


class TagViewSet(viewsets.ModelViewSet):
    """
    Same CRUD patterns as MuscleGroupViewSet.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def get_queryset(self):
        user = self.request.user
        return Tag.objects.filter(
            models.Q(user=user) | models.Q(user__isnull=True)
        )