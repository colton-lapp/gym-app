from django.contrib.auth import get_user_model
from rest_framework import serializers
from ..models import (
    MuscleGroup,
    Tag,
    Exercise,
    GymSession,
    ExerciseCompletion,
    ExerciseEvent,
)
from .exercises import ExerciseSerializer
User = get_user_model()


class ExerciseEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseEvent
        fields = [
            "id",
            "completion",
            "order_index",
            "reps",
            "duration_seconds",
            "weight",
            "distance",
            "resistance",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ExerciseCompletionSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        source="exercise",
        queryset=Exercise.objects.all(),
        write_only=True,
    )
    events = ExerciseEventSerializer(many=True, read_only=True)

    class Meta:
        model = ExerciseCompletion
        fields = [
            "id",
            "session",
            "exercise",
            "exercise_id",
            "note",
            "events",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        return ExerciseCompletion.objects.create(user=user, **validated_data)
