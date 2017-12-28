from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import get_language

from speedy.core.profiles.widgets import Widget
from speedy.match.accounts.models import SiteProfile as MatchSiteProfile


class UserOnSpeedyMatchWidget(Widget):
    template_name = 'profiles/user_on_speedy_match_widget.html'
    permission_required = 'accounts.view_profile_info'

    def get_entity_speedy_match_profile(self):
        return self.entity.get_profile(model=MatchSiteProfile)

    def get_viewer_speedy_match_profile(self):
        if not self.viewer.is_authenticated:
            return None
        return self.viewer.get_profile(model=MatchSiteProfile)

    def is_match(self):
        if not self.viewer.is_authenticated:
            return False
        if self.viewer == self.entity:
            return False
        return self.get_entity_speedy_match_profile().get_matching_rank(self.get_viewer_speedy_match_profile()) > MatchSiteProfile.RANK_0

    def get_context_data(self):
        cd = super().get_context_data()
        language_code = get_language()
        SPEEDY_MATCH_SITE_ID = settings.SITE_PROFILES['match']['site_id']
        cd.update({
            'is_match': self.is_match(),
            'speedy_match_url': Site.objects.get(id=SPEEDY_MATCH_SITE_ID).domain,
            'LANGUAGE_CODE': language_code
        })
        return cd
