from datetime import timedelta, datetime, timezone, date

from django.utils.timezone import now
from django.utils.translation import get_language, gettext_lazy as _
from django.views import generic
from django.db.models import Count

from speedy.core.base.utils import get_age_ranges_match
from speedy.core.admin.mixins import OnlyAdminMixin
from speedy.core.accounts.utils import get_site_profile_model
from speedy.core.accounts.models import User
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


class AdminMatchesListView(OnlyAdminMixin, generic.ListView):
    template_name = 'admin/matches/match_list.html'
    # page_size = 96
    page_size = 250
    paginate_by = page_size

    def get_total_number_of_active_members_text(self):
        language_code = get_language()
        total_number_of_active_members = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
        ).count()
        total_number_of_female_active_members = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            gender=User.GENDER_FEMALE,
        ).count()
        total_number_of_male_active_members = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            gender=User.GENDER_MALE,
        ).count()
        total_number_of_other_active_members = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            gender=User.GENDER_OTHER,
        ).count()
        total_number_of_active_members_in_the_last_week = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=7),
        ).count()
        total_number_of_female_active_members_in_the_last_week = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=7),
            gender=User.GENDER_FEMALE,
        ).count()
        total_number_of_male_active_members_in_the_last_week = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=7),
            gender=User.GENDER_MALE,
        ).count()
        total_number_of_other_active_members_in_the_last_week = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=7),
            gender=User.GENDER_OTHER,
        ).count()
        total_number_of_active_members_in_the_last_month = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=30),
        ).count()
        total_number_of_female_active_members_in_the_last_month = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=30),
            gender=User.GENDER_FEMALE,
        ).count()
        total_number_of_male_active_members_in_the_last_month = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=30),
            gender=User.GENDER_MALE,
        ).count()
        total_number_of_other_active_members_in_the_last_month = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=30),
            gender=User.GENDER_OTHER,
        ).count()
        total_number_of_active_members_in_the_last_four_months = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=120),
        ).count()
        total_number_of_female_active_members_in_the_last_four_months = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=120),
            gender=User.GENDER_FEMALE,
        ).count()
        total_number_of_male_active_members_in_the_last_four_months = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=120),
            gender=User.GENDER_MALE,
        ).count()
        total_number_of_other_active_members_in_the_last_four_months = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=120),
            gender=User.GENDER_OTHER,
        ).count()
        total_number_of_active_members_in_the_last_two_years = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=720),
        ).count()
        total_number_of_female_active_members_in_the_last_two_years = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=720),
            gender=User.GENDER_FEMALE,
        ).count()
        total_number_of_male_active_members_in_the_last_two_years = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=720),
            gender=User.GENDER_MALE,
        ).count()
        total_number_of_other_active_members_in_the_last_two_years = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=720),
            gender=User.GENDER_OTHER,
        ).count()
        total_number_of_active_members_text = _("Admin: The total number of active members on the site is {total_number_of_active_members} ({total_number_of_female_active_members} females, {total_number_of_male_active_members} males, {total_number_of_other_active_members} others; {total_percent_of_female_active_members} females, {total_percent_of_male_active_members} males, {total_percent_of_other_active_members} others), of which {total_number_of_active_members_in_the_last_week} members ({total_number_of_female_active_members_in_the_last_week} females, {total_number_of_male_active_members_in_the_last_week} males, {total_number_of_other_active_members_in_the_last_week} others; {total_percent_of_female_active_members_in_the_last_week} females, {total_percent_of_male_active_members_in_the_last_week} males, {total_percent_of_other_active_members_in_the_last_week} others) entered the site in the last week, {total_number_of_active_members_in_the_last_month} members ({total_number_of_female_active_members_in_the_last_month} females, {total_number_of_male_active_members_in_the_last_month} males, {total_number_of_other_active_members_in_the_last_month} others; {total_percent_of_female_active_members_in_the_last_month} females, {total_percent_of_male_active_members_in_the_last_month} males, {total_percent_of_other_active_members_in_the_last_month} others) entered the site in the last month, {total_number_of_active_members_in_the_last_four_months} members ({total_number_of_female_active_members_in_the_last_four_months} females, {total_number_of_male_active_members_in_the_last_four_months} males, {total_number_of_other_active_members_in_the_last_four_months} others; {total_percent_of_female_active_members_in_the_last_four_months} females, {total_percent_of_male_active_members_in_the_last_four_months} males, {total_percent_of_other_active_members_in_the_last_four_months} others) entered the site in the last four months, and {total_number_of_active_members_in_the_last_two_years} members ({total_number_of_female_active_members_in_the_last_two_years} females, {total_number_of_male_active_members_in_the_last_two_years} males, {total_number_of_other_active_members_in_the_last_two_years} others; {total_percent_of_female_active_members_in_the_last_two_years} females, {total_percent_of_male_active_members_in_the_last_two_years} males, {total_percent_of_other_active_members_in_the_last_two_years} others) entered the site in the last two years.").format(
            total_number_of_active_members='{:,}'.format(total_number_of_active_members),
            total_number_of_female_active_members='{:,}'.format(total_number_of_female_active_members),
            total_number_of_male_active_members='{:,}'.format(total_number_of_male_active_members),
            total_number_of_other_active_members='{:,}'.format(total_number_of_other_active_members),
            total_percent_of_female_active_members='{:,.1f}%'.format(round(float(total_number_of_female_active_members) / float(total_number_of_active_members) * 100, 1) if (total_number_of_active_members > 0) else 0),
            total_percent_of_male_active_members='{:,.1f}%'.format(round(float(total_number_of_male_active_members) / float(total_number_of_active_members) * 100, 1) if (total_number_of_active_members > 0) else 0),
            total_percent_of_other_active_members='{:,.1f}%'.format(round(float(total_number_of_other_active_members) / float(total_number_of_active_members) * 100, 1) if (total_number_of_active_members > 0) else 0),
            total_number_of_active_members_in_the_last_week='{:,}'.format(total_number_of_active_members_in_the_last_week),
            total_number_of_female_active_members_in_the_last_week='{:,}'.format(total_number_of_female_active_members_in_the_last_week),
            total_number_of_male_active_members_in_the_last_week='{:,}'.format(total_number_of_male_active_members_in_the_last_week),
            total_number_of_other_active_members_in_the_last_week='{:,}'.format(total_number_of_other_active_members_in_the_last_week),
            total_percent_of_female_active_members_in_the_last_week='{:,.1f}%'.format(round(float(total_number_of_female_active_members_in_the_last_week) / float(total_number_of_active_members_in_the_last_week) * 100, 1) if (total_number_of_active_members_in_the_last_week > 0) else 0),
            total_percent_of_male_active_members_in_the_last_week='{:,.1f}%'.format(round(float(total_number_of_male_active_members_in_the_last_week) / float(total_number_of_active_members_in_the_last_week) * 100, 1) if (total_number_of_active_members_in_the_last_week > 0) else 0),
            total_percent_of_other_active_members_in_the_last_week='{:,.1f}%'.format(round(float(total_number_of_other_active_members_in_the_last_week) / float(total_number_of_active_members_in_the_last_week) * 100, 1) if (total_number_of_active_members_in_the_last_week > 0) else 0),
            total_number_of_active_members_in_the_last_month='{:,}'.format(total_number_of_active_members_in_the_last_month),
            total_number_of_female_active_members_in_the_last_month='{:,}'.format(total_number_of_female_active_members_in_the_last_month),
            total_number_of_male_active_members_in_the_last_month='{:,}'.format(total_number_of_male_active_members_in_the_last_month),
            total_number_of_other_active_members_in_the_last_month='{:,}'.format(total_number_of_other_active_members_in_the_last_month),
            total_percent_of_female_active_members_in_the_last_month='{:,.1f}%'.format(round(float(total_number_of_female_active_members_in_the_last_month) / float(total_number_of_active_members_in_the_last_month) * 100, 1) if (total_number_of_active_members_in_the_last_month > 0) else 0),
            total_percent_of_male_active_members_in_the_last_month='{:,.1f}%'.format(round(float(total_number_of_male_active_members_in_the_last_month) / float(total_number_of_active_members_in_the_last_month) * 100, 1) if (total_number_of_active_members_in_the_last_month > 0) else 0),
            total_percent_of_other_active_members_in_the_last_month='{:,.1f}%'.format(round(float(total_number_of_other_active_members_in_the_last_month) / float(total_number_of_active_members_in_the_last_month) * 100, 1) if (total_number_of_active_members_in_the_last_month > 0) else 0),
            total_number_of_active_members_in_the_last_four_months='{:,}'.format(total_number_of_active_members_in_the_last_four_months),
            total_number_of_female_active_members_in_the_last_four_months='{:,}'.format(total_number_of_female_active_members_in_the_last_four_months),
            total_number_of_male_active_members_in_the_last_four_months='{:,}'.format(total_number_of_male_active_members_in_the_last_four_months),
            total_number_of_other_active_members_in_the_last_four_months='{:,}'.format(total_number_of_other_active_members_in_the_last_four_months),
            total_percent_of_female_active_members_in_the_last_four_months='{:,.1f}%'.format(round(float(total_number_of_female_active_members_in_the_last_four_months) / float(total_number_of_active_members_in_the_last_four_months) * 100, 1) if (total_number_of_active_members_in_the_last_four_months > 0) else 0),
            total_percent_of_male_active_members_in_the_last_four_months='{:,.1f}%'.format(round(float(total_number_of_male_active_members_in_the_last_four_months) / float(total_number_of_active_members_in_the_last_four_months) * 100, 1) if (total_number_of_active_members_in_the_last_four_months > 0) else 0),
            total_percent_of_other_active_members_in_the_last_four_months='{:,.1f}%'.format(round(float(total_number_of_other_active_members_in_the_last_four_months) / float(total_number_of_active_members_in_the_last_four_months) * 100, 1) if (total_number_of_active_members_in_the_last_four_months > 0) else 0),
            total_number_of_active_members_in_the_last_two_years='{:,}'.format(total_number_of_active_members_in_the_last_two_years),
            total_number_of_female_active_members_in_the_last_two_years='{:,}'.format(total_number_of_female_active_members_in_the_last_two_years),
            total_number_of_male_active_members_in_the_last_two_years='{:,}'.format(total_number_of_male_active_members_in_the_last_two_years),
            total_number_of_other_active_members_in_the_last_two_years='{:,}'.format(total_number_of_other_active_members_in_the_last_two_years),
            total_percent_of_female_active_members_in_the_last_two_years='{:,.1f}%'.format(round(float(total_number_of_female_active_members_in_the_last_two_years) / float(total_number_of_active_members_in_the_last_two_years) * 100, 1) if (total_number_of_active_members_in_the_last_two_years > 0) else 0),
            total_percent_of_male_active_members_in_the_last_two_years='{:,.1f}%'.format(round(float(total_number_of_male_active_members_in_the_last_two_years) / float(total_number_of_active_members_in_the_last_two_years) * 100, 1) if (total_number_of_active_members_in_the_last_two_years > 0) else 0),
            total_percent_of_other_active_members_in_the_last_two_years='{:,.1f}%'.format(round(float(total_number_of_other_active_members_in_the_last_two_years) / float(total_number_of_active_members_in_the_last_two_years) * 100, 1) if (total_number_of_active_members_in_the_last_two_years > 0) else 0),
        )
        total_number_of_active_members_registered_in_the_last_week = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            date_created__gte=now() - timedelta(days=7),
        ).count()
        total_number_of_active_members_registered_in_the_last_month = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            date_created__gte=now() - timedelta(days=30),
        ).count()
        total_number_of_active_members_registered_in_the_last_four_months = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            date_created__gte=now() - timedelta(days=120),
        ).count()
        total_number_of_active_members_registered_more_than_four_months_ago = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            date_created__lte=now() - timedelta(days=120),
        ).count()
        total_number_of_active_members_registered_in_the_last_two_years = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            date_created__gte=now() - timedelta(days=720),
        ).count()
        total_number_of_active_members_registered_more_than_two_years_ago = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            date_created__lte=now() - timedelta(days=720),
        ).count()
        total_number_of_active_members_registered_before_2019_08_01 = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            date_created__lte=datetime.strptime('2019-08-01 00:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc),
        ).count()
        total_number_of_active_members_text += "\n"
        total_number_of_active_members_text += "\n"
        total_number_of_active_members_text += _("Admin: {total_number_of_active_members_registered_in_the_last_week} active members registered in the last week. {total_number_of_active_members_registered_in_the_last_month} active members registered in the last month. {total_number_of_active_members_registered_in_the_last_four_months} active members registered in the last four months. {total_number_of_active_members_registered_more_than_four_months_ago} active members registered more than four months ago. {total_number_of_active_members_registered_in_the_last_two_years} active members registered in the last two years. {total_number_of_active_members_registered_more_than_two_years_ago} active members registered more than two years ago. {total_number_of_active_members_registered_before_2019_08_01} active members registered before 1 August 2019.").format(
            total_number_of_active_members_registered_in_the_last_week='{:,}'.format(total_number_of_active_members_registered_in_the_last_week),
            total_number_of_active_members_registered_in_the_last_month='{:,}'.format(total_number_of_active_members_registered_in_the_last_month),
            total_number_of_active_members_registered_in_the_last_four_months='{:,}'.format(total_number_of_active_members_registered_in_the_last_four_months),
            total_number_of_active_members_registered_more_than_four_months_ago='{:,}'.format(total_number_of_active_members_registered_more_than_four_months_ago),
            total_number_of_active_members_registered_in_the_last_two_years='{:,}'.format(total_number_of_active_members_registered_in_the_last_two_years),
            total_number_of_active_members_registered_more_than_two_years_ago='{:,}'.format(total_number_of_active_members_registered_more_than_two_years_ago),
            total_number_of_active_members_registered_before_2019_08_01='{:,}'.format(total_number_of_active_members_registered_before_2019_08_01),
        )
        total_number_of_active_members_text += "\n"
        today = date.today()
        for year in range(2010, today.year + 2):
            total_number_of_active_members_registered_in_year = User.objects.active(
                speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
                speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
                speedy_match_site_profile__active_languages__contains=[language_code],
                date_created__gte=datetime.strptime('{year}-01-01 00:00:00'.format(year=year), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc),
                date_created__lt=datetime.strptime('{year}-01-01 00:00:00'.format(year=year + 1), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc),
            ).count()
            total_number_of_active_members_text += "\n"
            total_number_of_active_members_text += _("Admin: {total_number_of_active_members_registered_in_year} active members registered in {year}.").format(
                total_number_of_active_members_registered_in_year='{:,}'.format(total_number_of_active_members_registered_in_year),
                year=year,
            )
        age_interval = 5
        if (self.request.GET.get('age_interval')):
            age_interval = int(self.request.GET.get('age_interval'))
        total_number_of_active_members_text += "\n"
        for age in range(SpeedyMatchSiteProfile.settings.MIN_AGE_TO_MATCH_ALLOWED, SpeedyMatchSiteProfile.settings.MAX_AGE_TO_MATCH_ALLOWED + 20, age_interval):
            age_ranges = get_age_ranges_match(min_age=age, max_age=age + (age_interval - 1))
            total_number_of_active_members_in_age_range = User.objects.active(
                speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
                speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
                speedy_match_site_profile__active_languages__contains=[language_code],
                date_of_birth__range=age_ranges,
            ).count()
            total_number_of_female_active_members_in_age_range = User.objects.active(
                speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
                speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
                speedy_match_site_profile__active_languages__contains=[language_code],
                date_of_birth__range=age_ranges,
                gender=User.GENDER_FEMALE,
            ).count()
            total_number_of_male_active_members_in_age_range = User.objects.active(
                speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
                speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
                speedy_match_site_profile__active_languages__contains=[language_code],
                date_of_birth__range=age_ranges,
                gender=User.GENDER_MALE,
            ).count()
            total_number_of_other_active_members_in_age_range = User.objects.active(
                speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
                speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
                speedy_match_site_profile__active_languages__contains=[language_code],
                date_of_birth__range=age_ranges,
                gender=User.GENDER_OTHER,
            ).count()
            if ((total_number_of_active_members_in_age_range > 0) or (age < 100)):
                total_number_of_active_members_text += "\n"
                total_percent_of_female_active_members_in_age_range = round(float(total_number_of_female_active_members_in_age_range) / float(total_number_of_active_members_in_age_range) * 100, 1) if (total_number_of_active_members_in_age_range > 0) else 0
                total_percent_of_male_active_members_in_age_range = round(float(total_number_of_male_active_members_in_age_range) / float(total_number_of_active_members_in_age_range) * 100, 1) if (total_number_of_active_members_in_age_range > 0) else 0
                total_percent_of_other_active_members_in_age_range = round(float(total_number_of_other_active_members_in_age_range) / float(total_number_of_active_members_in_age_range) * 100, 1) if (total_number_of_active_members_in_age_range > 0) else 0
                if (total_number_of_active_members_in_age_range > 0):
                    if ((total_percent_of_female_active_members_in_age_range < 35) or (total_percent_of_male_active_members_in_age_range < 35)):
                        if (total_number_of_active_members_in_age_range >= 20):
                            total_number_of_active_members_text += '<span style="color: red;">'
                        else:
                            total_number_of_active_members_text += '<span style="color: #b10515;">'
                    else:
                        if (total_number_of_active_members_in_age_range >= 10):
                            total_number_of_active_members_text += '<span>'
                        else:
                            total_number_of_active_members_text += '<span style="color: #b10515;">'
                else:
                    total_number_of_active_members_text += '<span style="color: green;">'
                total_number_of_active_members_text += _("Admin: {total_number_of_active_members_in_age_range} ({total_number_of_female_active_members_in_age_range} females, {total_number_of_male_active_members_in_age_range} males, {total_number_of_other_active_members_in_age_range} others) active members aged {min_age} to {max_age} ({total_percent_of_female_active_members_in_age_range} females, {total_percent_of_male_active_members_in_age_range} males, {total_percent_of_other_active_members_in_age_range} others).").format(
                    total_number_of_active_members_in_age_range='{:,}'.format(total_number_of_active_members_in_age_range),
                    total_number_of_female_active_members_in_age_range='{:,}'.format(total_number_of_female_active_members_in_age_range),
                    total_number_of_male_active_members_in_age_range='{:,}'.format(total_number_of_male_active_members_in_age_range),
                    total_number_of_other_active_members_in_age_range='{:,}'.format(total_number_of_other_active_members_in_age_range),
                    total_percent_of_female_active_members_in_age_range='{:,.1f}%'.format(total_percent_of_female_active_members_in_age_range),
                    total_percent_of_male_active_members_in_age_range='{:,.1f}%'.format(total_percent_of_male_active_members_in_age_range),
                    total_percent_of_other_active_members_in_age_range='{:,.1f}%'.format(total_percent_of_other_active_members_in_age_range),
                    min_age='{:,}'.format(age),
                    max_age='{:,}'.format(age + (age_interval - 1)),
                )
                total_number_of_active_members_text += '</span>'
        total_number_of_active_members_text += "\n"
        for age in range(SpeedyMatchSiteProfile.settings.MIN_AGE_TO_MATCH_ALLOWED, SpeedyMatchSiteProfile.settings.MAX_AGE_TO_MATCH_ALLOWED + 20, age_interval):
            age_ranges = get_age_ranges_match(min_age=age, max_age=age + (age_interval - 1))
            total_number_of_active_members_in_age_range_in_the_last_four_months = User.objects.active(
                speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
                speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
                speedy_match_site_profile__active_languages__contains=[language_code],
                speedy_match_site_profile__last_visit__gte=now() - timedelta(days=120),
                date_of_birth__range=age_ranges,
            ).count()
            total_number_of_female_active_members_in_age_range_in_the_last_four_months = User.objects.active(
                speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
                speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
                speedy_match_site_profile__active_languages__contains=[language_code],
                speedy_match_site_profile__last_visit__gte=now() - timedelta(days=120),
                date_of_birth__range=age_ranges,
                gender=User.GENDER_FEMALE,
            ).count()
            total_number_of_male_active_members_in_age_range_in_the_last_four_months = User.objects.active(
                speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
                speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
                speedy_match_site_profile__active_languages__contains=[language_code],
                speedy_match_site_profile__last_visit__gte=now() - timedelta(days=120),
                date_of_birth__range=age_ranges,
                gender=User.GENDER_MALE,
            ).count()
            total_number_of_other_active_members_in_age_range_in_the_last_four_months = User.objects.active(
                speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
                speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
                speedy_match_site_profile__active_languages__contains=[language_code],
                speedy_match_site_profile__last_visit__gte=now() - timedelta(days=120),
                date_of_birth__range=age_ranges,
                gender=User.GENDER_OTHER,
            ).count()
            if ((total_number_of_active_members_in_age_range_in_the_last_four_months > 0) or (age < 100)):
                total_number_of_active_members_text += "\n"
                total_percent_of_female_active_members_in_age_range_in_the_last_four_months = round(float(total_number_of_female_active_members_in_age_range_in_the_last_four_months) / float(total_number_of_active_members_in_age_range_in_the_last_four_months) * 100, 1) if (total_number_of_active_members_in_age_range_in_the_last_four_months > 0) else 0
                total_percent_of_male_active_members_in_age_range_in_the_last_four_months = round(float(total_number_of_male_active_members_in_age_range_in_the_last_four_months) / float(total_number_of_active_members_in_age_range_in_the_last_four_months) * 100, 1) if (total_number_of_active_members_in_age_range_in_the_last_four_months > 0) else 0
                total_percent_of_other_active_members_in_age_range_in_the_last_four_months = round(float(total_number_of_other_active_members_in_age_range_in_the_last_four_months) / float(total_number_of_active_members_in_age_range_in_the_last_four_months) * 100, 1) if (total_number_of_active_members_in_age_range_in_the_last_four_months > 0) else 0
                if (total_number_of_active_members_in_age_range_in_the_last_four_months > 0):
                    if ((total_percent_of_female_active_members_in_age_range_in_the_last_four_months < 35) or (total_percent_of_male_active_members_in_age_range_in_the_last_four_months < 35)):
                        if (total_number_of_active_members_in_age_range_in_the_last_four_months >= 20):
                            total_number_of_active_members_text += '<span style="color: red;">'
                        else:
                            total_number_of_active_members_text += '<span style="color: #b10515;">'
                    else:
                        if (total_number_of_active_members_in_age_range_in_the_last_four_months >= 10):
                            total_number_of_active_members_text += '<span>'
                        else:
                            total_number_of_active_members_text += '<span style="color: #b10515;">'
                else:
                    total_number_of_active_members_text += '<span style="color: green;">'
                total_number_of_active_members_text += _("Admin: {total_number_of_active_members_in_age_range_in_the_last_four_months} ({total_number_of_female_active_members_in_age_range_in_the_last_four_months} females, {total_number_of_male_active_members_in_age_range_in_the_last_four_months} males, {total_number_of_other_active_members_in_age_range_in_the_last_four_months} others) active members aged {min_age} to {max_age} ({total_percent_of_female_active_members_in_age_range_in_the_last_four_months} females, {total_percent_of_male_active_members_in_age_range_in_the_last_four_months} males, {total_percent_of_other_active_members_in_age_range_in_the_last_four_months} others) entered the site in the last four months.").format(
                    total_number_of_active_members_in_age_range_in_the_last_four_months='{:,}'.format(total_number_of_active_members_in_age_range_in_the_last_four_months),
                    total_number_of_female_active_members_in_age_range_in_the_last_four_months='{:,}'.format(total_number_of_female_active_members_in_age_range_in_the_last_four_months),
                    total_number_of_male_active_members_in_age_range_in_the_last_four_months='{:,}'.format(total_number_of_male_active_members_in_age_range_in_the_last_four_months),
                    total_number_of_other_active_members_in_age_range_in_the_last_four_months='{:,}'.format(total_number_of_other_active_members_in_age_range_in_the_last_four_months),
                    total_percent_of_female_active_members_in_age_range_in_the_last_four_months='{:,.1f}%'.format(total_percent_of_female_active_members_in_age_range_in_the_last_four_months),
                    total_percent_of_male_active_members_in_age_range_in_the_last_four_months='{:,.1f}%'.format(total_percent_of_male_active_members_in_age_range_in_the_last_four_months),
                    total_percent_of_other_active_members_in_age_range_in_the_last_four_months='{:,.1f}%'.format(total_percent_of_other_active_members_in_age_range_in_the_last_four_months),
                    min_age='{:,}'.format(age),
                    max_age='{:,}'.format(age + (age_interval - 1)),
                )
                total_number_of_active_members_text += '</span>'
        return total_number_of_active_members_text

    def get_queryset(self):
        SiteProfile = get_site_profile_model()
        language_code = get_language()
        filter_dict = dict(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
        )
        annotate_list = list()
        if (self.request.GET.get('likes_from_user')):
            annotate_list.append(Count('likes_from_user', distinct=True))
            filter_dict["likes_from_user__count__gte"] = int(self.request.GET.get('likes_from_user'))
        if (self.request.GET.get('likes_to_user')):
            annotate_list.append(Count('likes_to_user', distinct=True))
            filter_dict["likes_to_user__count__gte"] = int(self.request.GET.get('likes_to_user'))
        qs = User.objects.active().annotate(*annotate_list).filter(**filter_dict).order_by('-{}__last_visit'.format(SiteProfile.RELATED_NAME))
        return qs

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'matches_list': cd['object_list'],
            'total_number_of_active_members_text': self.get_total_number_of_active_members_text(),
        })
        return cd


