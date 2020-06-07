from datetime import timedelta, datetime, timezone, date

from django.utils.translation import get_language, gettext_lazy as _
from django.utils.timezone import now
from django.views import generic

from speedy.core.admin.mixins import OnlyAdminMixin
from speedy.core.accounts.utils import get_site_profile_model
from speedy.core.accounts.models import User
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


class AdminMatchesListView(OnlyAdminMixin, generic.ListView):
    template_name = 'admin/matches/match_list.html'
    # page_size = 96
    page_size = 250
    paginate_by = page_size

    @staticmethod
    def get_total_number_of_active_members_text():
        language_code = get_language()
        total_number_of_active_members = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
        ).count()
        total_number_of_active_members_in_the_last_week = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=7),
        ).count()
        total_number_of_active_members_in_the_last_month = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=30),
        ).count()
        total_number_of_active_members_in_the_last_four_months = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=120),
        ).count()
        total_number_of_active_members_text = _("Admin: The total number of active members on the site is {total_number_of_active_members}, of which {total_number_of_active_members_in_the_last_week} members entered the site in the last week, {total_number_of_active_members_in_the_last_month} members entered the site in the last month, and {total_number_of_active_members_in_the_last_four_months} members entered the site in the last four months.").format(
            total_number_of_active_members='{:,}'.format(total_number_of_active_members),
            total_number_of_active_members_in_the_last_week='{:,}'.format(total_number_of_active_members_in_the_last_week),
            total_number_of_active_members_in_the_last_month='{:,}'.format(total_number_of_active_members_in_the_last_month),
            total_number_of_active_members_in_the_last_four_months='{:,}'.format(total_number_of_active_members_in_the_last_four_months),
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
        total_number_of_active_members_registered_before_2019_08_01 = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            date_created__lte=datetime.strptime('2019-08-01 00:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc),
        ).count()
        total_number_of_active_members_text += "\n"
        total_number_of_active_members_text += "\n"
        total_number_of_active_members_text += _("Admin: {total_number_of_active_members_registered_in_the_last_week} active members registered in the last week. {total_number_of_active_members_registered_in_the_last_month} active members registered in the last month. {total_number_of_active_members_registered_in_the_last_four_months} active members registered in the last four months. {total_number_of_active_members_registered_more_than_four_months_ago} active members registered more than four months ago. {total_number_of_active_members_registered_before_2019_08_01} active members registered before 1 August 2019.").format(
            total_number_of_active_members_registered_in_the_last_week='{:,}'.format(total_number_of_active_members_registered_in_the_last_week),
            total_number_of_active_members_registered_in_the_last_month='{:,}'.format(total_number_of_active_members_registered_in_the_last_month),
            total_number_of_active_members_registered_in_the_last_four_months='{:,}'.format(total_number_of_active_members_registered_in_the_last_four_months),
            total_number_of_active_members_registered_more_than_four_months_ago='{:,}'.format(total_number_of_active_members_registered_more_than_four_months_ago),
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
        return total_number_of_active_members_text

    def get_queryset(self):
        SiteProfile = get_site_profile_model()
        language_code = get_language()
        qs = User.objects.active(
            speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
        ).order_by('-{}__last_visit'.format(SiteProfile.RELATED_NAME))
        return qs

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'matches_list': cd['object_list'],
            'total_number_of_active_members_text': self.get_total_number_of_active_members_text(),
        })
        return cd


