from django.utils.translation import get_language

from speedy.core.base.utils import get_age_ranges_match
from speedy.core.base.models import BaseManager
from speedy.core.accounts.models import User


class SiteProfileManager(BaseManager):
    def get_matches(self, user_profile):
        age_ranges = get_age_ranges_match(min_age=user_profile.min_age_match, max_age=user_profile.max_age_match)
        language_code = get_language()
        qs = User.objects.active(gender__in=user_profile.gender_to_match, date_of_birth__range=age_ranges, speedy_match_site_profile__active_languages__contains=language_code).exclude(pk=user_profile.user_id).prefetch_related(self.model.RELATED_NAME).distinct().order_by('-speedy_match_site_profile__last_visit')
        u1_list = [user for user in qs if ((user.speedy_match_profile.is_active) and (user_profile._1___get_matching_rank_quick_without_testing(other_profile=user.speedy_match_profile) > self.model.RANK_0))]
        u1_list = sorted(u1_list, key=lambda user: (user.speedy_match_profile._1___rank, user.speedy_match_profile.last_visit), reverse=True)
        user_list = []
        matches_list = []
        rank_list = {
            self.model.RANK_1: [],
            self.model.RANK_2: [],
            self.model.RANK_3: [],
            self.model.RANK_4: [],
            self.model.RANK_5: [],
        }
        for user in u1_list:
            if ((len(matches_list) < 360) or (len(user_list) < 600)):
                user_list.append(user)
                if ((user.speedy_match_profile.is_active) and (user_profile.get_matching_rank(other_profile=user.speedy_match_profile) > self.model.RANK_0)):
                    matches_list.append(user)
                    rank_list[user.speedy_match_profile.rank].append(user)
        matches_list = sorted(matches_list, key=lambda user: (user.speedy_match_profile.rank, user.speedy_match_profile.last_visit), reverse=True)
        return matches_list


