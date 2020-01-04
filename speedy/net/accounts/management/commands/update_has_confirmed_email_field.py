import logging
from datetime import timedelta

from django.core.management import BaseCommand
from django.utils.timezone import now

from speedy.core.accounts.models import User, UserEmailAddress

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            user._update_has_confirmed_email_field()


