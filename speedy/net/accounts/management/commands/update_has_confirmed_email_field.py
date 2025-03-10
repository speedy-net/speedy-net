import logging

from django.core.management import BaseCommand

from speedy.core.accounts.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    A Django management command to update the has_confirmed_email field for all users.

    This command iterates over all users and updates their has_confirmed_email field.

    Methods:
        handle(*args, **options): Executes the command to update the has_confirmed_email field.
    """

    def handle(self, *args, **options):
        """
        Executes the command to update the has_confirmed_email field for all users.

        This method iterates over all users, reloads each user from the database,
        and updates their has_confirmed_email field.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.
        """
        users = User.objects.all()
        for u in users:
            # Users might have changed in the database, load them again.
            user = User.objects.get(pk=u.pk)
            user._update_has_confirmed_email_field()


