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
        if (django_settings.GET_IP_ADDRESS_IPAPI_INFO):
            users = User.objects.exclude(
                last_ip_address_used__isnull=True,
            ).filter(
                last_ip_address_used_ipapi_time__isnull=True,
                last_ip_address_used_date_updated__isnull=False,
                last_ip_address_used_date_updated__lte=(now() - timedelta(minutes=4)),
            ).distinct(
            ).order_by('last_ip_address_used_date_updated')[:36]
            for user in users:
                if ((user.last_ip_address_used is not None) and (user.last_ip_address_used_ipapi_time is None) and (user.last_ip_address_used_date_updated is not None) and (user.last_ip_address_used_date_updated <= (now() - timedelta(minutes=4)))):
                    # If there are other users with the same last_ip_address_used, and they have already made an original ipapi call in the last 30 days, then use their results.
                    ip_address_original_ipapi_call = True
                    ip_address_raw_ipapi_results = None
                    try:
                        original_users = User.objects.filter(
                            last_ip_address_used=user.last_ip_address_used,
                            last_ip_address_used_original_ipapi_call=True,
                            last_ip_address_used_ipapi_time__isnull=False,
                            last_ip_address_used_raw_ipapi_results__isnull=False,
                            last_ip_address_used_ipapi_time__lte=(now() - timedelta(minutes=4)),
                            last_ip_address_used_ipapi_time__gte=(now() - timedelta(days=30)),
                        ).exclude(
                            pk__in=[user.pk],
                        ).distinct(
                        ).order_by('last_ip_address_used_date_updated')[:36]
                        for original_user in original_users:
                            if ((ip_address_original_ipapi_call is True) and (original_user.last_ip_address_used == user.last_ip_address_used) and (original_user.last_ip_address_used_original_ipapi_call is True) and (original_user.last_ip_address_used_ipapi_time is not None) and (original_user.last_ip_address_used_raw_ipapi_results is not None) and (user.last_ip_address_used_ipapi_time <= (now() - timedelta(minutes=4))) and (user.last_ip_address_used_ipapi_time >= (now() - timedelta(days=30)))):
                                ip_address_original_ipapi_call = False
                                ip_address_raw_ipapi_results = original_user.last_ip_address_used_raw_ipapi_results
                        # Otherwise, make the original ipapi call.
                        if (ip_address_original_ipapi_call is True):
                            url = "https://api.ipapi.com/api/{ip_address}?access_key={ipapi_api_access_key}".format(
                                ip_address=user.last_ip_address_used,
                                ipapi_api_access_key=django_settings.IPAPI_API_ACCESS_KEY,
                            )
                            ip_address_raw_ipapi_results = json.loads(urllib.request.urlopen(url).read())
                        if (not ("error" in ip_address_raw_ipapi_results)):
                            user.last_ip_address_used_original_ipapi_call = ip_address_original_ipapi_call
                            user.last_ip_address_used_raw_ipapi_results = ip_address_raw_ipapi_results
                            user.last_ip_address_used_ipapi_time = now()
                            user.save()
                            if (("latitude" in ip_address_raw_ipapi_results) and ("longitude" in ip_address_raw_ipapi_results)):
                                city = "unknown city"
                                region = "unknown region"
                                country = "unknown country"
                                continent = "unknown continent"
                                if ("city" in ip_address_raw_ipapi_results):
                                    city = ip_address_raw_ipapi_results["city"]
                                if ("region_name" in ip_address_raw_ipapi_results):
                                    region = ip_address_raw_ipapi_results["region_name"]
                                if ("country_name" in ip_address_raw_ipapi_results):
                                    country = ip_address_raw_ipapi_results["country_name"]
                                if ("continent_name" in ip_address_raw_ipapi_results):
                                    continent = ip_address_raw_ipapi_results["continent_name"]
                                logger.debug("get_ip_address_ipapi_info::info ok, info saved. user={user}, {user_name} (last_ip_address_used={last_ip_address_used}) is located in {city}, {region}, {country}, {continent}. (registered {registered_days_ago} days ago, original_ipapi_call={original_ipapi_call}).".format(
                                    user=user,
                                    user_name=user.name,
                                    last_ip_address_used=user.last_ip_address_used,
                                    city=city,
                                    region=region,
                                    country=country,
                                    continent=continent,
                                    registered_days_ago=(now() - user.date_created).days,
                                    original_ipapi_call=ip_address_original_ipapi_call,
                                ))
                            else:
                                logger.error("get_ip_address_ipapi_info::info not ok, info saved. ip_address_raw_ipapi_results={ip_address_raw_ipapi_results}, user={user} (registered {registered_days_ago} days ago, original_ipapi_call={original_ipapi_call}).".format(
                                    ip_address_raw_ipapi_results=ip_address_raw_ipapi_results,
                                    user=user,
                                    registered_days_ago=(now() - user.date_created).days,
                                    original_ipapi_call=ip_address_original_ipapi_call,
                                ))
                        else:
                            logger.error("get_ip_address_ipapi_info::info not ok, info not saved. ip_address_raw_ipapi_results={ip_address_raw_ipapi_results}, user={user} (registered {registered_days_ago} days ago, original_ipapi_call={original_ipapi_call}).".format(
                                ip_address_raw_ipapi_results=ip_address_raw_ipapi_results,
                                user=user,
                                registered_days_ago=(now() - user.date_created).days,
                                original_ipapi_call=ip_address_original_ipapi_call,
                            ))

                    except Exception as e:
                        logger.error('get_ip_address_ipapi_info::user={user}, Exception={e} (registered {registered_days_ago} days ago, original_ipapi_call={original_ipapi_call}).'.format(
                            user=user,
                            e=str(e),
                            registered_days_ago=(now() - user.date_created).days,
                            original_ipapi_call=ip_address_original_ipapi_call,
                        ))


