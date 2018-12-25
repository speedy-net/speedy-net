from speedy.core.accounts.models import User
from speedy.core.base.utils import get_age_ranges_match

from speedy.core.base.models import BaseManager


class SiteProfileManager(BaseManager):
    def get_matches(self, user_profile):
        age_ranges = get_age_ranges_match(min_age=user_profile.min_age_match, max_age=user_profile.max_age_match)
        qs = User.objects.active(gender__in=user_profile.gender_to_match, date_of_birth__range=age_ranges).exclude(pk=user_profile.user_id).distinct()

        qs = [user for user in qs if ((user_profile.get_matching_rank(other_profile=user.speedy_match_profile) > self.model.RANK_0) and (user.speedy_match_profile.is_active))]

        qs = sorted(qs, key=lambda user: (user.speedy_match_profile.rank, user.speedy_match_profile.last_visit), reverse=True)
        return qs


