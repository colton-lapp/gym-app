from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import (
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