from datetime import timedelta

from django.core.management import BaseCommand
from django.utils.timezone import now

from speedy.core.accounts.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.filter(date_created__lte=(now() - timedelta(days=10))).exclude(is_staff=True)

        for user in users:
            if (not (user.is_staff)):
                if (not (user.has_confirmed_email())):
                    user.delete()


