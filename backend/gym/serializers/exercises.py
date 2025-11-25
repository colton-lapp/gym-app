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



class ExerciseSerializer(serializers.ModelSerializer):
    muscle_groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=MuscleGroup.objects.all(),
        required=False,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=False,
    )

    class Meta:
        model = Exercise
        fields = [
            "id",
            "name",
            "image",
            "exercise_type",
            "muscle_groups",
            "tags",
            "track_reps",
            "track_weight",
            "track_distance",
            "track_duration",
            "track_resistance",
            "track_notes",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        muscle_groups = validated_data.pop("muscle_groups", [])
        tags = validated_data.pop("tags", [])
        exercise = Exercise.objects.create(user=user, **validated_data)
        exercise.muscle_groups.set(muscle_groups)
        exercise.tags.set(tags)
        return exercise

    def update(self, instance, validated_data):
        muscle_groups = validated_data.pop("muscle_groups", None)
        tags = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if muscle_groups is not None:
            instance.muscle_groups.set(muscle_groups)
        if tags is not None:
            instance.tags.set(tags)
        return instance

