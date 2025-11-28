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
        fields = ["id", "name", "icon", "is_default"]
    def update(self, instance, validated_data):
        if instance.user is None:
            raise serializers.ValidationError("Default muscle groups cannot be edited.")
        return super().update(instance, validated_data)
    def perform_destroy(self, instance):
        if instance.user is None:
            raise serializers.ValidationError("Default muscle groups cannot be deleted.")
        return super().perform_destroy(instance)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "icon", "is_default"]
    def update(self, instance, validated_data):
        if instance.user is None:
            raise serializers.ValidationError("Default tags cannot be edited.")
        return super().update(instance, validated_data)
    def perform_destroy(self, instance):
        if instance.user is None:
            raise serializers.ValidationError("Default tags cannot be deleted.")
        return super().perform_destroy(instance)   
    
class MuscleGroupMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = MuscleGroup
        fields = ["id", "name", "icon"]
    def update(self, instance, validated_data):
        if instance.user is None:
            raise serializers.ValidationError("Default muscle groups cannot be edited.")
        return super().update(instance, validated_data)
    def perform_destroy(self, instance):
        if instance.user is None:
            raise serializers.ValidationError("Default muscle groups cannot be deleted.")
        return super().perform_destroy(instance)
     
class TagMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "icon"]
    def update(self, instance, validated_data):
        if instance.user is None:
            raise serializers.ValidationError("Default tags cannot be edited.")
        return super().update(instance, validated_data)
    def perform_destroy(self, instance):
        if instance.user is None:
            raise serializers.ValidationError("Default tags cannot be deleted.")
        return super().perform_destroy(instance)