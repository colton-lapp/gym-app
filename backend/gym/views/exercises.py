from rest_framework import viewsets, permissions, decorators, response, status
from ..models import Exercise
from ..serializers.exercises import ExerciseSerializer
from ..serializers.events import ExerciseCompletionSerializer


class ExerciseViewSet(viewsets.ModelViewSet):
    """
    Endpoints:
    - GET  /api/exercises/
      TODO filters:
        ?tag={id}
        ?muscle_group={id}
        ?search={string}
        ?recent=true (order by last completion)
    - POST /api/exercises/
    - PATCH /api/exercises/{id}/
    - DELETE /api/exercises/{id}/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExerciseSerializer
    queryset = Exercise.objects.all()

    def get_queryset(self):
        user = self.request.user
        qs = Exercise.objects.filter(user=user)

        # Filter by tag
        tag_id = self.request.query_params.get("tag_id")
        if tag_id:
            qs = qs.filter(tags__id=tag_id)

        # Filter by muscle group
        mg_id = self.request.query_params.get("muscle_group_id")
        if mg_id:
            qs = qs.filter(muscle_groups__id=mg_id)

        # Search by name
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)

        # Sort
        ordering = self.request.query_params.get("ordering")
        if ordering == "name":
            qs = qs.order_by("name")
        elif ordering == "recent":
            # last completion time; annotate, then order
            from django.db.models import Max
            qs = qs.annotate(
                last_completed_at=Max("completions__created_at")
            ).order_by("-last_completed_at", "name")

        return qs

    @decorators.action(detail=True, methods=["get"])
    def last_completion(self, request, pk=None):
        """
        GET /api/exercises/{id}/last_completion/

        Returns:
        - The last ExerciseCompletion for this exercise for the current user
        - Or 404 if none exists
        """
        exercise = self.get_object()
        completion = exercise.last_completion_for_user(request.user)
        if not completion:
            return response.Response(
                {"detail": "No completions yet."},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = ExerciseCompletionSerializer(completion).data
        return response.Response(data)