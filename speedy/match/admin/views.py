from datetime import timedelta

from django.utils.translation import get_language, gettext_lazy as _
from django.utils.timezone import now
from django.views import generic

from speedy.core.admin.mixins import OnlyAdminMixin
from speedy.core.accounts.utils import get_site_profile_model
from speedy.core.accounts.models import User
from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


class AdminMatchesListView(OnlyAdminMixin, generic.ListView):
    template_name = 'admin/matches/match_list.html'
    page_size = 96
    paginate_by = page_size

    def get_total_number_of_active_members_text(self):
        language_code = get_language()
        total_number_of_active_members = User.objects.active(
            speedy_match_site_profile__active_languages__contains=[language_code],
        ).count()
        total_number_of_active_members_in_the_last_week = User.objects.active(
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=7),
        ).count()
        total_number_of_active_members_in_the_last_month = User.objects.active(
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=30),
        ).count()
        total_number_of_active_members_in_the_last_four_months = User.objects.active(
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=120),
        ).count()
        total_number_of_active_members_text = _("Admin: The total number of active members on the site is {total_number_of_active_members}, of which {total_number_of_active_members_in_the_last_week} members entered the site in the last week, {total_number_of_active_members_in_the_last_month} members entered the site in the last month, and {total_number_of_active_members_in_the_last_four_months} members entered the site in the last four months.").format(
            total_number_of_active_members=total_number_of_active_members,
            total_number_of_active_members_in_the_last_week=total_number_of_active_members_in_the_last_week,
            total_number_of_active_members_in_the_last_month=total_number_of_active_members_in_the_last_month,
            total_number_of_active_members_in_the_last_four_months=total_number_of_active_members_in_the_last_four_months,
        )
        return total_number_of_active_members_text

    def get_queryset(self):
        SiteProfile = get_site_profile_model()
        language_code = get_language()
        qs = User.objects.active(
            speedy_match_site_profile__active_languages__contains=[language_code],
        ).prefetch_related(SpeedyNetSiteProfile.RELATED_NAME, SpeedyMatchSiteProfile.RELATED_NAME).distinct().order_by('-{}__last_visit'.format(SiteProfile.RELATED_NAME))
        return qs

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'matches_list': cd['object_list'],
            'total_number_of_active_members_text': self.get_total_number_of_active_members_text(),
        })
        return cd


