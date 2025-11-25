from django.shortcuts import render
from rest_framework import viewsets, permissions, decorators, response, status
from django.db import models
from django.utils import timezone
from .models import (
    MuscleGroup,
    Tag,
    Exercise,
    GymSession,
    ExerciseCompletion,
    ExerciseEvent,
)
from .serializers import (
    MuscleGroupSerializer,
    TagSerializer,
    ExerciseSerializer,
    GymSessionSerializer,
    ExerciseCompletionSerializer,
    ExerciseEventSerializer,
)


class BaseUserQuerysetMixin:
    """
    Filter queryset to objects owned by request.user.
    Used by most ViewSets.
    """
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if hasattr(qs.model, "user"):
            return qs.filter(user=user)
        return qs.none()


class MuscleGroupViewSet(BaseUserQuerysetMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = MuscleGroup.objects.all()
    serializer_class = MuscleGroupSerializer

    def get_queryset(self):
        user = self.request.user
        return MuscleGroup.objects.filter(models.Q(user=user) | models.Q(user__isnull=True))


class TagViewSet(BaseUserQuerysetMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        user = self.request.user
        return Tag.objects.filter(models.Q(user=user) | models.Q(user__isnull=True))


class ExerciseViewSet(BaseUserQuerysetMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

    def get_queryset(self):
        user = self.request.user
        return Exercise.objects.filter(user=user)


class GymSessionViewSet(BaseUserQuerysetMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = GymSession.objects.all()
    serializer_class = GymSessionSerializer

    def get_queryset(self):
        return GymSession.objects.filter(user=self.request.user)

    @decorators.action(detail=False, methods=["get"])
    def current(self, request):
        session = (
            GymSession.objects.filter(user=request.user, end_time__isnull=True)
            .order_by("-start_time")
            .first()
        )
        if not session:
            return response.Response({"detail": "No open session."}, status=404)
        return response.Response(self.get_serializer(session).data)

    @decorators.action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        session = self.get_object()
        session.close(save=True)
        return response.Response(self.get_serializer(session).data)


class ExerciseCompletionViewSet(BaseUserQuerysetMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ExerciseCompletion.objects.all()
    serializer_class = ExerciseCompletionSerializer

    def get_queryset(self):
        return ExerciseCompletion.objects.filter(user=self.request.user)

    @decorators.action(detail=True, methods=["get"])
    def last_values(self, request, pk=None):
        completion = self.get_object()
        return response.Response(completion.last_values_for_prefill())


class ExerciseEventViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ExerciseEvent.objects.all()
    serializer_class = ExerciseEventSerializer

    def get_queryset(self):
        return ExerciseEvent.objects.filter(completion__user=self.request.user)

    def perform_create(self, serializer):
        completion = serializer.validated_data["completion"]
        if completion.user != self.request.user:
            raise permissions.PermissionDenied("Not your completion")
        serializer.save()