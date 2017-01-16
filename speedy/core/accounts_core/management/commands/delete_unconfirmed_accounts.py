from datetime import timedelta

from django.core.management import BaseCommand
from django.utils.timezone import now

from speedy.core.accounts_core.models import UserEmailAddress


class Command(BaseCommand):
    def handle(self, *args, **options):
        emails = UserEmailAddress.objects.filter(is_confirmed=False, date_created__lte=(now() - timedelta(days=10)))
        for email in emails:
            has_confirmed_email = email.user.email_addresses.filter(is_confirmed=True).exists()
            if has_confirmed_email:
                pass
            else:
                email.user.delete()
