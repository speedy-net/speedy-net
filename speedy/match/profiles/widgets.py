from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import get_language

from speedy.core.profiles.widgets import Widget
from speedy.core.accounts.models import User
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


class UserExtraDetailsWidget(Widget):
    template_name = 'profiles/user_extra_info_widget.html'
    permission_required = 'accounts.view_profile_info'

    def get_context_data(self):
        cd = super().get_context_data()

        marital_status = "Unknown"
        marital_status_code = self.entity.profile.marital_status
        for status in MatchSiteProfile.MARITAL_STATUS_CHOICES:
            if status[0] == marital_status_code:
                marital_status = status[1]
                break

        smoking_choice = "Unknown"
        smoking_choice_code = self.entity.profile.smoking
        for choice in MatchSiteProfile.SMOKING_CHOICES:
            if choice[0] == smoking_choice_code:
                smoking_choice = choice[1]
                break

        diet = "Unknown"
        diet_code = self.entity.diet
        if diet_code != User.DIET_UNKNOWN:
            for choice in User.DIET_CHOICES:
                if choice[0] == diet_code:
                    diet = choice[1]
                    break

        genders_to_match = []
        gender_codes = self.entity.profile.gender_to_match
        for gender in User.GENDER_CHOICES:
            if gender[0] in gender_codes:
                genders_to_match.append(str(gender[1]))

        if len(genders_to_match) == 0:
            genders_to_match.append("None")

        cd.update({
            'marital_status': marital_status,
            'smoking_choice': smoking_choice,
            'diet': diet,
            'gender_to_match': ", ".join(genders_to_match),
        })
        return cd
