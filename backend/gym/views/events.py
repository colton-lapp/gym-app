from rest_framework import viewsets, permissions, decorators, response
from ..models import ExerciseEvent, ExerciseCompletion
from ..serializers.events import ExerciseEventSerializer, ExerciseCompletionSerializer


class ExerciseCompletionViewSet(viewsets.ModelViewSet):
    """
    Endpoints:
    - POST /api/exercise-completions/
      { session, exercise_id, note }
    - GET  /api/exercise-completions/{id}/
      returns events + info
    - PATCH /api/exercise-completions/{id}/
    - DELETE /api/exercise-completions/{id}/
    - GET /api/exercise-completions/{id}/last_values/
      for prefill UI values
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExerciseCompletionSerializer
    queryset = ExerciseCompletion.objects.all()

    def get_queryset(self):
        """
        Limit completions to the current user.
        """
        return ExerciseCompletion.objects.filter(user=self.request.user)

    @decorators.action(detail=True, methods=["get"])
    def last_values(self, request, pk=None):
        """
        TODO:
        - Call model method last_values_for_prefill()
        """
        completion = self.get_object()
        return response.Response(completion.last_values_for_prefill())


class ExerciseEventViewSet(viewsets.ModelViewSet):
    """
    Endpoints:
    - POST /api/events/
      { completion, reps/weight/duration/... }
    - GET /api/events/?completion={id}
      (TODO: manual filtering)
    - PATCH /api/events/{id}/
    - DELETE /api/events/{id}/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExerciseEventSerializer
    queryset = ExerciseEvent.objects.all()

    def get_queryset(self):
        """
        Limit to events belonging to user.
        """
        return ExerciseEvent.objects.filter(
            completion__user=self.request.user
        )

    def perform_create(self, serializer):
        """
        Ensure event belongs to user.
        """
        completion = serializer.validated_data["completion"]
        if completion.user != self.request.user:
            raise permissions.PermissionDenied("Not your completion")
        serializer.save()