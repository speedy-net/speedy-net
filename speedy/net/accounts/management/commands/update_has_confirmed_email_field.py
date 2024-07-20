import logging

from django.core.management import BaseCommand

from speedy.core.accounts.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.all()
        for u in users:
            # Users might have changed in the database, load them again.
            user = User.objects.get(pk=u.pk)
            user._update_has_confirmed_email_field()


