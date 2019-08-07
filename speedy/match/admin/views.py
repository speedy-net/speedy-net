from django.utils.translation import get_language
from django.views import generic

from speedy.core.admin.mixins import OnlyAdminMixin
from speedy.core.accounts.models import User
from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


class AdminMatchesListView(OnlyAdminMixin, generic.ListView):
    template_name = 'admin/matches/match_list.html'
    page_size = 24
    paginate_by = page_size

    def get_queryset(self):
        language_code = get_language()
        qs = User.objects.active(
            speedy_match_site_profile__active_languages__contains=[language_code],
        ).prefetch_related(SpeedyNetSiteProfile.RELATED_NAME, SpeedyMatchSiteProfile.RELATED_NAME).distinct().order_by('-speedy_match_site_profile__last_visit')
        return qs

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'matches_list': cd['object_list'],
        })
        return cd


