# gym/serializers/exercises.py

from rest_framework import serializers
from ..models import Exercise, MuscleGroup, Tag
from .categories import MuscleGroupMiniSerializer, TagMiniSerializer


class ExerciseSerializer(serializers.ModelSerializer):
    muscle_groups = MuscleGroupMiniSerializer(many=True, read_only=True)
    tags = TagMiniSerializer(many=True, read_only=True)

    muscle_group_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=MuscleGroup.objects.all(),
        required=False,
        source="muscle_groups",
    )

    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Tag.objects.all(),
        required=False,
        source="tags",
    )

    last_completed_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Exercise
        fields = [
            "id", "name", "image",
            "muscle_groups", "tags",
            "muscle_group_ids", "tag_ids",
            "track_reps", "track_weight", "track_distance",
            "track_duration", "track_resistance_string", "track_resistance_numeric", "track_notes",
            "last_completed_at", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "image", "muscle_groups", "tags",
                            "last_completed_at", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Must remove M2M data before model instance is created.
        Then add them afterward with .set()
        """
        user = self.context["request"].user
        
        muscle_groups = validated_data.pop("muscle_groups", [])
        tags = validated_data.pop("tags", [])

        exercise = Exercise.objects.create(user=user, **validated_data)
        if muscle_groups:
            exercise.muscle_groups.set(muscle_groups)
        if tags:
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