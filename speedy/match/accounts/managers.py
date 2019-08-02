from django.utils.translation import get_language

from speedy.core.base.utils import get_age_ranges_match
from speedy.core.base.models import BaseManager
from speedy.core.accounts.models import User


class SiteProfileManager(BaseManager):
    def get_matches(self, user_profile):
        age_ranges = get_age_ranges_match(min_age=user_profile.min_age_match, max_age=user_profile.max_age_match)
        language_code = get_language()
        qs = User.objects.active(gender__in=user_profile.gender_to_match, date_of_birth__range=age_ranges, speedy_match_site_profile__active_languages__contains=language_code).exclude(pk=user_profile.user_id).select_related(self.model.RELATED_NAME).distinct()
        # qs = list(qs) # ~~~~ TODO: remove this line!
        # for i in range(10): # ~~~~ TODO: remove this line!
        #     qs = qs + qs # ~~~~ TODO: remove this line!
        # qs = qs[:900] # ~~~~ TODO: remove this line!
        matches_list = [user for user in qs if ((user.speedy_match_profile.is_active) and (user_profile.get_matching_rank(other_profile=user.speedy_match_profile) > self.model.RANK_0))]
        matches_list = sorted(matches_list, key=lambda user: (user.speedy_match_profile.rank, user.speedy_match_profile.last_visit), reverse=True)
        return matches_list


