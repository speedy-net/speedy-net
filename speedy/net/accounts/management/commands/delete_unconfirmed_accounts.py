from datetime import timedelta

from django.core.management import BaseCommand
from django.utils.timezone import now

from speedy.core.accounts.models import UserEmailAddress


class Command(BaseCommand):
    def handle(self, *args, **options):
        emails = UserEmailAddress.objects.filter(is_confirmed=False, date_created__lte=(now() - timedelta(days=10))).exclude(user__is_staff=True)

        for email in emails:
            user = email.user
            if (not (user.is_staff)):
                if (not (user.has_confirmed_email())):
                    user.delete()


