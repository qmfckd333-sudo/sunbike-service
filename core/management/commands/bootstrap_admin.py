from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = "Create or reset admin user from environment variables"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("ADMIN_USERNAME", "admin")
        password = os.environ.get("ADMIN_PASSWORD", "admin1234")
        email = os.environ.get("ADMIN_EMAIL", "admin@example.com")

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        # ⭐ 핵심 부분 ⭐
        # 이미 존재해도 비밀번호를 무조건 다시 설정
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(
                f"Admin user '{username}' created."
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f"Admin user '{username}' password RESET."
            ))
