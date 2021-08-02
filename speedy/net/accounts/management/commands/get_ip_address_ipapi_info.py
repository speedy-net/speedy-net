import logging
import json
import urllib.request
from datetime import timedelta

from django.conf import settings as django_settings
from django.core.management import BaseCommand
from django.utils.timezone import now

from speedy.core.accounts.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.exclude(
            last_ip_address_used=None,
        ).filter(
            last_ip_address_used_ipapi_time=None,
            last_ip_address_used_date_updated__lte=(now() - timedelta(minutes=4)),
        ).distinct(
        ).order_by('last_ip_address_used_date_updated')
        for user in users:
            if ((user.last_ip_address_used is not None) and (user.last_ip_address_used_ipapi_time is None) and (user.last_ip_address_used_date_updated <= (now() - timedelta(minutes=4)))):
                try:
                    url = "https://api.ipapi.com/api/{ip_address}?access_key={ipapi_api_access_key}".format(
                        ip_address=user.last_ip_address_used,
                        ipapi_api_access_key=django_settings.IPAPI_API_ACCESS_KEY,
                    )
                    ip_address_raw_ipapi_results = json.loads(urllib.request.urlopen(url).read())
                    if (not ("error" in ip_address_raw_ipapi_results)):
                        user.last_ip_address_used_raw_ipapi_results = ip_address_raw_ipapi_results
                        user.last_ip_address_used_ipapi_time = now()
                        user.save()
                        if ("latitude" in ip_address_raw_ipapi_results) and ("longitude" in ip_address_raw_ipapi_results):
                            logger.debug("get_ip_address_ipapi_info::info ok, info saved. user={user}, registered {registered_days_ago} days ago).".format(
                                user=user,
                                registered_days_ago=(now() - user.date_created).days,
                            ))
                        else:
                            logger.error("get_ip_address_ipapi_info::info not ok, info saved. ip_address_raw_ipapi_results={ip_address_raw_ipapi_results}, user={user}, registered {registered_days_ago} days ago).".format(
                                ip_address_raw_ipapi_results=ip_address_raw_ipapi_results,
                                user=user,
                                registered_days_ago=(now() - user.date_created).days,
                            ))
                    else:
                        logger.error("get_ip_address_ipapi_info::info not ok, info not saved. ip_address_raw_ipapi_results={ip_address_raw_ipapi_results}, user={user}, registered {registered_days_ago} days ago).".format(
                            ip_address_raw_ipapi_results=ip_address_raw_ipapi_results,
                            user=user,
                            registered_days_ago=(now() - user.date_created).days,
                        ))

                except Exception as e:
                    logger.error('get_ip_address_ipapi_info::user={user}, Exception={e} (registered {registered_days_ago} days ago)'.format(
                        user=user,
                        e=str(e),
                        registered_days_ago=(now() - user.date_created).days,
                    ))


