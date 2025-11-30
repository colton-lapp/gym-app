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
    duration_value = serializers.IntegerField(
        required=False, write_only=True
    )
    duration_unit = serializers.ChoiceField(
        choices=["sec", "s", "min"],
        required=False,
        write_only=True,
    )

    class Meta:
        model = ExerciseEvent
        fields = [
            "id",
            "completion",
            "order_index",
            "reps",
            "duration_seconds",
            "duration_value",
            "duration_unit",
            "weight",
            "distance",
            "resistance_string",
            "resistance_numeric",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, attrs):
        duration_value = attrs.pop("duration_value", None)
        duration_unit = attrs.pop("duration_unit", None)

        if duration_value is not None and attrs.get("duration_seconds") is None:
            if duration_unit in ["min"]:
                attrs["duration_seconds"] = duration_value * 60
            else:  # default sec
                attrs["duration_seconds"] = duration_value

        return attrs


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
