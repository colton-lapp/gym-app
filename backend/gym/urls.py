from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MuscleGroupViewSet,
    TagViewSet,
    ExerciseViewSet,
    GymSessionViewSet,
    ExerciseCompletionViewSet,
    ExerciseEventViewSet,
)

router = DefaultRouter()
router.register("muscle-groups", MuscleGroupViewSet)
router.register("tags", TagViewSet)
router.register("exercises", ExerciseViewSet)
router.register("sessions", GymSessionViewSet)
router.register("exercise-completions", ExerciseCompletionViewSet)
router.register("events", ExerciseEventViewSet)

urlpatterns = [
    path("", include(router.urls)),
]