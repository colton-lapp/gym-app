# gym/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.db.models import Max

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MuscleGroup(TimestampedModel):
    """
    A muscle group category (e.g. 'Chest', 'Back').
    user = null => global/default category available to everyone.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="muscle_groups",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    icon = models.CharField(max_length=50, blank=True)  # Material/Iconify name

    class Meta:
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self):
        prefix = "Global" if self.user is None else f"{self.user}"
        return f"{self.name} ({prefix})"


class Tag(TimestampedModel):
    """
    A tag category (e.g. 'push', 'pull', 'cardio', 'machine').
    user = null => global/default tag.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exercise_tags",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    icon = models.CharField(max_length=50, blank=True)  # Material/Iconify name
    
    class Meta:
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self):
        prefix = "Global" if self.user is None else f"{self.user}"
        return f"{self.name} ({prefix})"


class Exercise(TimestampedModel):
    """
    Definition of an exercise (per user).
    Controls which fields are tracked on events.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exercises",
    )
    name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to="exercise_images/",
        null=True,
        blank=True,
    )
    muscle_groups = models.ManyToManyField(
        MuscleGroup,
        related_name="exercises",
        blank=True,
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="exercises",
        blank=True,
    )

    # Optional fields toggles – UI decides which inputs show up.
    track_reps = models.BooleanField(default=True)
    track_weight = models.BooleanField(default=False)
    track_distance = models.BooleanField(default=False)
    track_duration = models.BooleanField(default=False)
    track_resistance = models.BooleanField(default=False)
    track_notes = models.BooleanField(default=False)

    def last_completion_for_user(self, user):
        """
        Returns the most recent *previous* ExerciseCompletion for this exercise
        for the given user, skipping:
        - completions with no events
        - completions belonging to the current open session
        """
        return (
            self.completions
            .filter(
                user=user,
                events__isnull=False,             # must have sets/splits
                session__end_time__isnull=False,  # session must be CLOSED
            )
            .annotate(last_event_at=Max("events__created_at"))
            .order_by("-last_event_at")
            .first()
        )
    
    class Meta:
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.user})"


class GymSession(TimestampedModel):
    """
    A training session for a user.
    end_time = null => 'open' session.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gym_sessions",
    )
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_time"]

    def __str__(self):
        status = "open" if self.is_open else "closed"
        return f"Session {self.id} ({self.user}) [{status}]"

    @property
    def is_open(self) -> bool:
        return self.end_time is None

    def close(self, when=None, save=True):
        """
        Close the session. If no `when` is provided, you could
        choose last event time or now().
        """
        if when is None:
            last_event = (
                ExerciseEvent.objects
                .filter(completion__session=self)
                .order_by("-created_at")
                .first()
            )
            when = last_event.created_at if last_event else timezone.now()
        self.end_time = when
        if save:
            self.save()


class ExerciseCompletion(TimestampedModel):
    """
    A concrete instance of an Exercise within a specific GymSession.
    Holds its own note and set/split events.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exercise_completions",
    )
    session = models.ForeignKey(
        GymSession,
        on_delete=models.CASCADE,
        related_name="exercise_completions",
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.PROTECT,
        related_name="completions",
    )
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.exercise.name} in session {self.session_id} ({self.user})"

    def last_event(self):
        return self.events.order_by("-created_at").first()

    def last_values_for_prefill(self):
        """
        Helper for your “guess weight/reps/distance” feature.
        Returns a dict of the last event’s values.
        """
        last = self.last_event()
        if not last:
            return {}
        return {
            "reps": last.reps,
            "weight": last.weight,
            "distance": last.distance,
            "duration_seconds": last.duration_seconds,
            "resistance": last.resistance,
        }


class ExerciseEvent(TimestampedModel):
    """
    A set or split belonging to an ExerciseCompletion.
    Which fields matter is governed by Exercise.exercise_type
    and Exercise.track_* flags.
    """
    completion = models.ForeignKey(
        ExerciseCompletion,
        on_delete=models.CASCADE,
        related_name="events",
    )

    # To preserve an explicit order of sets/splits (1,2,3,...) if needed.
    order_index = models.PositiveIntegerField(default=1)

    # For sets
    reps = models.PositiveIntegerField(null=True, blank=True)

    # For splits or timed events (stored in seconds)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    # Common optional metrics
    weight = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
    )
    distance = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Distance in chosen unit (e.g. km, miles, etc.)",
    )
    resistance = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # Optional per-event note (if you decide you want it)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["completion", "order_index", "created_at"]

    def __str__(self):
        return f"Event {self.id} for {self.completion}"