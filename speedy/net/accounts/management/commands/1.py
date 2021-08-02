import logging
from datetime import timedelta

from django.core.management import BaseCommand
from django.utils.timezone import now

from speedy.core.accounts.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.exclude(
            last_ip_address_used__isnull=True,
        ).filter(
            last_ip_address_used_ipapi_time=None,
            last_ip_address_used_date_updated__lte=(now() - timedelta(minutes=5)),
        ).distinct(
        ).order_by('last_ip_address_used_date_updated')
        for user in users:
            if ((user.last_ip_address_used is not None) and (user.last_ip_address_used_ipapi_time is None) and (user.last_ip_address_used_date_updated <= (now() - timedelta(minutes=5)))):


