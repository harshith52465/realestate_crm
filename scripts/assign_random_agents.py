import os
import sys
import django
import random

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402
from properties.models import Property  # noqa: E402


def main() -> None:
    usernames = ["agent1", "agent2", "agent3", "agent4", "agent5"]
    agents = list(User.objects.filter(username__in=usernames))
    found = {u.username for u in agents}
    missing = [u for u in usernames if u not in found]
    if missing:
        print("Missing agents:", ", ".join(missing))
        return

    random.seed(42)
    props = list(Property.objects.order_by("id"))
    for p in props:
        p.assigned_to = random.choice(agents)
        p.save()
    print(f"Assigned {len(props)} properties to {len(agents)} agents")


if __name__ == "__main__":
    main()
