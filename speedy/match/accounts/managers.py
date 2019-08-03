from django.utils.translation import get_language

from speedy.core.base.utils import get_age_ranges_match
from speedy.core.base.models import BaseManager
from speedy.core.accounts.models import User


class SiteProfileManager(BaseManager):
    def get_matches(self, user_profile):
        user_profile._set_values_to_match()
        age_ranges = get_age_ranges_match(min_age=user_profile.min_age_to_match, max_age=user_profile.max_age_to_match)
        language_code = get_language()
        qs = User.objects.active(
            gender__in=user_profile.gender_to_match,
            diet__in=user_profile.diet_to_match,
            smoking_status__in=user_profile.smoking_status_to_match,
            relationship_status__in=user_profile.relationship_status_to_match,
            speedy_match_site_profile__gender_to_match__contains=[user_profile.user.gender],
            speedy_match_site_profile__diet_to_match__contains=[user_profile.user.diet],
            speedy_match_site_profile__smoking_status_to_match__contains=[user_profile.user.smoking_status],
            speedy_match_site_profile__relationship_status_to_match__contains=[user_profile.user.relationship_status],
            date_of_birth__range=age_ranges,
            speedy_match_site_profile__min_age_to_match__lte=user_profile.user.get_age(),
            speedy_match_site_profile__max_age_to_match__gte=user_profile.user.get_age(),
            speedy_match_site_profile__active_languages__contains=language_code,
        ).exclude(pk=user_profile.user_id).prefetch_related(self.model.RELATED_NAME).distinct().order_by('-speedy_match_site_profile__last_visit')
        matches_list = [user for user in qs[:2000] if ((user.speedy_match_profile.is_active) and (user_profile.get_matching_rank(other_profile=user.speedy_match_profile) > self.model.RANK_0))]
        matches_list = sorted(matches_list, key=lambda user: (user.speedy_match_profile.rank, user.speedy_match_profile.last_visit), reverse=True)
        matches_list = matches_list[:720]
        return matches_list


