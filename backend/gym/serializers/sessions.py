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

from .events import ExerciseCompletionSerializer
User = get_user_model()


class GymSessionSerializer(serializers.ModelSerializer):
    exercise_completions = ExerciseCompletionSerializer(
        many=True, read_only=True
    )
    is_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = GymSession
        fields = [
            "id",
            "start_time",
            "end_time",
            "is_open",
            "location",
            "note",
            "exercise_completions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "is_open"]

    def create(self, validated_data):
        user = self.context["request"].user
        return GymSession.objects.create(user=user, **validated_data)