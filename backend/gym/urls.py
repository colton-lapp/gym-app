from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.categories import MuscleGroupViewSet, TagViewSet
from .views.exercises import ExerciseViewSet
from .views.sessions import GymSessionViewSet
from .views.events import ExerciseCompletionViewSet, ExerciseEventViewSet

from .views.auth import signup, login, logout, me
from .views.locations import UserLocationViewSet



router = DefaultRouter()
router.register("muscle-groups", MuscleGroupViewSet)
router.register("tags", TagViewSet)
router.register("exercises", ExerciseViewSet)
router.register("sessions", GymSessionViewSet)
router.register("exercise-completions", ExerciseCompletionViewSet)
router.register("events", ExerciseEventViewSet)
router.register("locations", UserLocationViewSet)

urlpatterns = [
    path("", include(router.urls)),

    path("auth/signup/", signup, name="signup"),
    path("auth/login/", login, name="login"),
    path("auth/logout/", logout, name="logout"),
    path("auth/me/", me, name="me"),
]