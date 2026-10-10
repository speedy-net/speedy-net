"""
Utility functions for the Speedy Net accounts app, such as the text with the total number of active members.
"""
from datetime import timedelta

from django.utils import formats
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from speedy.core.accounts.models import User


def get_total_number_of_active_members_text():
    """
    Get a human-readable text describing the total number of active members on the site, and how many of them visited in the last week.

    The text is only generated (non-empty) if at least 300 members were active in the last four months and at least 50 members were active in the last week; otherwise an empty string is returned.

    :return: The text describing the total number of active members, or an empty string if the thresholds are not met.
    :rtype: str
    """
    total_number_of_active_members_in_the_last_four_months = User.objects.active(
        speedy_net_site_profile__is_active=True,
        has_confirmed_email=True,
        speedy_net_site_profile__last_visit__gte=now() - timedelta(days=120),
    ).count()
    total_number_of_active_members_in_the_last_week = User.objects.active(
        speedy_net_site_profile__is_active=True,
        has_confirmed_email=True,
        speedy_net_site_profile__last_visit__gte=now() - timedelta(days=7),
    ).count()
    # We only display this information on the website if the numbers are at least 300 and 50.
    if ((total_number_of_active_members_in_the_last_four_months >= 300) and (total_number_of_active_members_in_the_last_week >= 50)):
        total_number_of_active_members_text = _("The total number of active members on the site is {total_number_of_active_members_in_the_last_four_months}, of which {total_number_of_active_members_in_the_last_week} members entered the site in the last week.").format(
            total_number_of_active_members_in_the_last_four_months=formats.number_format(value=total_number_of_active_members_in_the_last_four_months),
            total_number_of_active_members_in_the_last_week=formats.number_format(value=total_number_of_active_members_in_the_last_week),
        )
    else:
        total_number_of_active_members_text = ""
    return total_number_of_active_members_text


