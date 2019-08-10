import logging
from datetime import timedelta

from django.core.management import BaseCommand
from django.utils.timezone import now

from speedy.core.accounts.models import UserEmailAddress

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        emails = UserEmailAddress.objects.filter(is_confirmed=False, date_created__lte=(now() - timedelta(days=5)), confirmation_sent__lte=1).exclude(confirmation_token='')
        for email in emails:
            user = email.user
            if (email.date_created <= now() - timedelta(days=5)):
                if ((email.is_confirmed is False) and (email.confirmation_sent <= 1)):
                    if (user.is_active):
                        logger.debug("Sending confirmation to email {} of user {}. Confirmation sent {} times, Added on {}.".format(email, user, email.confirmation_sent, email.date_created))
                        email.send_confirmation_email()


