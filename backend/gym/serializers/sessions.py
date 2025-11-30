from django.contrib.auth import get_user_model
from rest_framework import serializers
from ..serializers.locations import UserLocationSerializer
from ..models import (
    MuscleGroup,
    Tag,
    Exercise,
    GymSession,
    ExerciseCompletion,
    ExerciseEvent,
    UserLocation
)

from .events import ExerciseCompletionSerializer
User = get_user_model()


class GymSessionSerializer(serializers.ModelSerializer):
    location = UserLocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        source="location",
        queryset=UserLocation.objects.all(), 
        write_only=True,
        allow_null=True,
        required=False,
    )
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
            "note",
            "exercise_completions",
            "created_at",
            "updated_at",
            "location",     
            "location_id",   
        ]
        read_only_fields = ["created_at", "updated_at", "is_open"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            # Limit to locations owned by current user
            self.fields["location_id"].queryset = UserLocation.objects.for_user(
                request.user
            )
