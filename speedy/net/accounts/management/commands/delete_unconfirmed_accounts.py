import logging
from datetime import timedelta

from django.core.management import BaseCommand
from django.utils.timezone import now

from speedy.core.accounts.models import User, UserEmailAddress

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        emails = UserEmailAddress.objects.filter(is_confirmed=False, date_created__lte=(now() - timedelta(days=10)), confirmation_sent__gte=2).exclude(user__is_staff=True)
        for email in emails:
            user = email.user
            if (not (user.is_staff)):
                if (email.date_created <= now() - timedelta(days=10)):
                    if ((email.is_confirmed is False) and (email.confirmation_sent >= 2)):
                        logger.warning("Deleting email {} of user {} - unconfirmed. Confirmation sent {} times, Added on {}.".format(email, user, email.confirmation_sent, email.date_created))
                        email.delete()

        users = User.objects.filter(date_created__lte=(now() - timedelta(days=14)), has_confirmed_email=False).exclude(is_staff=True)
        for user in users:
            if (not (user.is_staff)):
                if (user.date_created <= now() - timedelta(days=14)):
                    user._update_has_confirmed_email_field()
                    if (not (user.has_confirmed_email)):
                        try:
                            logger.warning("Deleting user {} - no confirmed email. Registered on {}.".format(user, user.date_created))
                            user.delete()
                        except Exception as e:
                            logger.error("Can't delete user {} - exception {}.".format(user, e))


