from speedy.core.accounts.models import User
from speedy.core.base.utils import get_age_ranges_match

from speedy.core.base.models import BaseManager


class SiteProfileManager(BaseManager):
    def get_matches(self, user_profile):
        age_ranges = get_age_ranges_match(user_profile.min_age_match, user_profile.max_age_match)
        qs = User.objects.active(gender__in=user_profile.gender_to_match, date_of_birth__range=age_ranges).exclude(pk=user_profile.user_id).distinct()

        qs = [user for user in qs if (user_profile.get_matching_rank(other_profile=user.profile) > self.model.RANK_0) and user.profile.is_active]

        qs = sorted(qs, key=lambda user: (user.profile.rank, user.profile.last_visit), reverse=True)
        return qs

