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
from accounts.models import Profile  # noqa: E402
from properties.models import Property  # noqa: E402


def main() -> None:
    usernames = ["agent1", "agent2", "agent3", "agent4", "agent5"]
    created = []
    for u in usernames:
        if not User.objects.filter(username=u).exists():
            user = User.objects.create_user(
                username=u,
                password="agent123",
                email=f"{u}@example.com",
            )
            user.is_staff = True
            user.save()
            Profile.objects.get_or_create(user=user)
            created.append(u)

    random.seed(42)
    agents = list(User.objects.filter(username__in=usernames))
    props = list(Property.objects.order_by("id"))
    for p in props:
        p.assigned_to = random.choice(agents)
        p.save()

    print("Created agents:", ", ".join(created) if created else "none")
    print("Assigned", len(props), "properties")


if __name__ == "__main__":
    main()
