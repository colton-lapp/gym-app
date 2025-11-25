from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.categories import MuscleGroupViewSet, TagViewSet
from .views.exercises import ExerciseViewSet
from .views.sessions import GymSessionViewSet
from .views.events import ExerciseCompletionViewSet, ExerciseEventViewSet

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