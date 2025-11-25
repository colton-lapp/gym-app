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

User = get_user_model()


class MuscleGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MuscleGroup
        fields = ["id", "name", "is_default"]

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "is_default"]