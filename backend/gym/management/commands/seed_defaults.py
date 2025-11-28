from django.core.management.base import BaseCommand
from gym.models import Tag, MuscleGroup

DEFAULT_TAGS = [
    ("push", "sym_o_arrow_circle_up"),
    ("pull", "sym_o_arrow_circle_down"),
    ("cardio", "sym_o_favorite"),
    ("machine", "sym_o_precision_manufacturing"),
    ("physical therapy", "sym_o_personal_injury"),
]

DEFAULT_MUSCLE_GROUPS = [
    ("Chest", "sym_o_rib_cage"),
    ("Back", "sym_o_orthopedics"),
    ("Shoulders", "sym_o_person_2"),
    ("Arms", "sym_o_humerus_alt"),
    ("Legs", "sym_o_tibia_alt"),
    ("Core", "sym_o_format_align_center"),
    ("Full Body", "sym_o_all_inclusive"),
    ("Cardio", "sym_o_directions_run"),
]


class Command(BaseCommand):
    help = "Ensures default tags and muscle groups exist and have correct icons."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Ensuring defaults..."))

        for name, icon in DEFAULT_TAGS:
            obj, created = Tag.objects.update_or_create(
                user=None,
                name=name,
                defaults={"icon": icon, "is_default": True},
            )
            if created:
                self.stdout.write(f"Created tag: {name}")
            else:
                self.stdout.write(f"Updated tag: {name}")

        for name, icon in DEFAULT_MUSCLE_GROUPS:
            obj, created = MuscleGroup.objects.update_or_create(
                user=None,
                name=name,
                defaults={"icon": icon, "is_default": True},
            )
            if created:
                self.stdout.write(f"Created muscle group: {name}")
            else:
                self.stdout.write(f"Updated muscle group: {name}")

        self.stdout.write(self.style.SUCCESS("Defaults ensured safely."))