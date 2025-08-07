import logging

from django.conf import settings as django_settings
from django.core.management import BaseCommand
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
    from speedy.net.accounts import utils
elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
    from speedy.match.accounts import utils
else:
    raise NotImplementedError("Utility functions for logging total number of active members are not implemented for this site.")

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    A custom Django management command for logging the total number of active members.

    This class extends the `BaseCommand` class provided by Django to implement a custom
    management command. It uses a utility function to retrieve the total number of active
    members and logs the result.

    Methods:
        handle(*args, **options): Logs the total number of active members by calling a utility function.
    """

    def handle(self, *args, **options):
        """
        Logs the total number of active members.

        This method calls a utility function to retrieve the total number of active members
        and logs the result at the debug level.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.
        """
        site = Site.objects.get_current()
        logger.debug("{site_name}::log_total_number_of_active_members_text:: {total_number_of_active_members_text}".format(
            site_name=_(site.name),
            total_number_of_active_members_text=utils.get_total_number_of_active_members_text(),
        ))


