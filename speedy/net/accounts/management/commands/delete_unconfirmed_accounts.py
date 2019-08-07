import logging
from datetime import timedelta

from django.core.management import BaseCommand
from django.utils.timezone import now

from speedy.core.accounts.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.filter(date_created__lte=(now() - timedelta(days=10))).exclude(is_staff=True)

        for user in users:
            if (not (user.is_staff)):
                if (not (user.has_confirmed_email())):
                    logger.warning("Deleting user {} - no confirmed email. Registered on {}.".format(user, user.date_created))
                    user.delete()


