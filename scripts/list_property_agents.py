import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from properties.models import Property  # noqa: E402


def main() -> None:
    qs = Property.objects.select_related("assigned_to").order_by("id")
    for p in qs:
        agent = p.assigned_to.username if p.assigned_to else "UNASSIGNED"
        print(f"{p.id}: {p.title} -> {agent}")


if __name__ == "__main__":
    main()
