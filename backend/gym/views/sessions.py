from rest_framework import viewsets, permissions, decorators, response, status
from ..models import GymSession
from ..serializers.sessions import GymSessionSerializer
from django.utils import timezone

class GymSessionViewSet(viewsets.ModelViewSet):
    """
    Endpoints:
    - GET  /api/sessions/            list sessions
    - POST /api/sessions/            create session
    - GET  /api/sessions/{id}/       session details
    - PATCH /api/sessions/{id}/      update note/location
    - POST /api/sessions/{id}/close/ close session
    - GET  /api/sessions/current/    get active open session
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GymSessionSerializer
    queryset = GymSession.objects.all()

    def get_queryset(self):
        """
        Only return sessions for the logged-in user.
        """
        return GymSession.objects.filter(user=self.request.user)

    @decorators.action(detail=False, methods=["get"])
    def current(self, request):
        """
        TODO:
        - Fetch open session (end_time=None)
        - Return 404 if none exists
        """
        session = GymSession.objects.filter(
            user=request.user, end_time__isnull=True
        ).order_by("-start_time").first()

        if not session:
            return response.Response({"detail": "No open session."}, status=404)

        return response.Response(self.get_serializer(session).data)

    @decorators.action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        """
        TODO:
        - Mark session closed
        - Default to last event timestamp if needed
        """
        session = self.get_object()
        session.close(save=True)
        return response.Response(self.get_serializer(session).data)
    
    def perform_create(self, serializer):
        """
        Custom logic when starting a new session:
        - Close any other open sessions for this user
        - Create a new session belonging to this user
        """
        user = self.request.user

        # TODO (decide behavior): 
        # Option A: auto-close existing open sessions
        GymSession.objects.filter(user=user, end_time__isnull=True).update(
            end_time=timezone.now()
        )

        # Option B (alternative): if open exists, raise error instead:
        # if GymSession.objects.filter(user=user, end_time__isnull=True).exists():
        #     raise ValidationError("You already have an open session.")

        serializer.save(user=user)

    @decorators.action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        """
        POST /api/sessions/{id}/reopen/

        Behavior:
        - Close any currently open session
        - Set end_time=None on this session
        """
        user = request.user
        session = self.get_object()

        # Close any other open session
        GymSession.objects.filter(user=user, end_time__isnull=True).exclude(
            id=session.id
        ).update(end_time=timezone.now())

        # Reopen this one
        session.end_time = None
        session.save()

        return response.Response(self.get_serializer(session).data)