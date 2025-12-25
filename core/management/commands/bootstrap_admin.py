import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create an admin user if it does not exist. Controlled by env vars ADMIN_USERNAME/ADMIN_PASSWORD/ADMIN_EMAIL."

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get("ADMIN_USERNAME", "admin")
        password = os.environ.get("ADMIN_PASSWORD", "admin1234")
        email = os.environ.get("ADMIN_EMAIL", "")
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f"Admin '{username}' already exists."))
            return
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Admin '{username}' created."))
