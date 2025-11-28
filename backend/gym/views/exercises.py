# gym/api/exercises.py
from django.db.models import Max, Q
from rest_framework import viewsets, permissions, decorators, response, status
from ..models import Exercise
from ..serializers.exercises import ExerciseSerializer
from ..serializers.events import ExerciseCompletionSerializer

class ExerciseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExerciseSerializer
    queryset = Exercise.objects.all()

    def get_queryset(self):
        user = self.request.user

        qs = (
            Exercise.objects
            .filter(user=user)
            .annotate(
                # last completion time (any completion; if you prefer last closed-with-events only,
                # you can copy the logic from last_completion_for_user)
                last_completed_at=Max("completions__created_at")
            )
        )

        # Filter by tag
        tag_id = self.request.query_params.get("tag_id")
        if tag_id:
            qs = qs.filter(tags__id=tag_id)

        # Filter by muscle group
        mg_id = self.request.query_params.get("muscle_group_id")
        if mg_id:
            qs = qs.filter(muscle_groups__id=mg_id)

        # Search by name, muscle group, or tag
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(muscle_groups__name__icontains=search)
                | Q(tags__name__icontains=search)
            ).distinct()

        # Sort
        ordering = self.request.query_params.get("ordering")
        if ordering == "name":
            qs = qs.order_by("name")
        elif ordering == "recent":
            qs = qs.order_by("-last_completed_at", "name")
        else:
            qs = qs.order_by("name")

        return qs

    @decorators.action(detail=True, methods=["get"])
    def last_completion(self, request, pk=None):
        exercise = self.get_object()
        completion = exercise.last_completion_for_user(request.user)
        if not completion:
            return response.Response(
                {"detail": "No completions yet."},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = ExerciseCompletionSerializer(completion).data
        return response.Response(data)