from django.core.management.base import BaseCommand
from gym.models import Tag, MuscleGroup

# Stored as full usable <q-icon :name="...">
DEFAULT_TAGS = [
    ("push", "sym_o_arrow_circle_up"),
    ("pull", "sym_o_arrow_circle_down"),
    ("cardio", "sym_o_favorite"),
    ("machine", "sym_o_precision_manufacturing"),
    ("physical therapy", "sym_o_personal_injury"),
]

DEFAULT_MUSCLE_GROUPS = [
    ("Chest", "sym_o_rib_cage"),
    ("Back",  "sym_o_orthopedics"),
    ("Shoulders", "sym_o_person_2"),
    ("Arms", "sym_o_humerus_alt"),
    ("Legs", "sym_o_tibia_alt"),
    ("Core", "sym_o_format_align_center"),
    ("Full Body", "sym_o_all_inclusive"),
    ("Cardio", "sym_o_directions_run"),
]


class Command(BaseCommand):
    help = "Deletes ALL tags + muscle groups and seeds defaults with correct q-icon names"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Wiping tags + muscle groups..."))

        Tag.objects.all().delete()
        MuscleGroup.objects.all().delete()

        for name, icon in DEFAULT_TAGS:
            Tag.objects.create(user=None, name=name, icon=icon, is_default=True)

        for name, icon in DEFAULT_MUSCLE_GROUPS:
            MuscleGroup.objects.create(user=None, name=name, icon=icon, is_default=True)

        self.stdout.write(self.style.SUCCESS("Seed complete — defaults reset + icons READY"))