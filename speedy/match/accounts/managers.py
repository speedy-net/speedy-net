import logging
import hashlib
from datetime import date, datetime

from django.utils.translation import get_language
from django.utils.timezone import now

from speedy.core.base.utils import get_age_ranges_match, string_is_not_empty
from speedy.core.base.managers import BaseManager
from speedy.core.accounts.models import User

logger = logging.getLogger(__name__)


class SiteProfileManager(BaseManager):
    # Same function as user.speedy_match_profile.get_matching_rank(other_profile=other_user.speedy_match_profile), but more optimized.
    def _get_rank(self, user, other_user, blocked_users_ids, blocking_users_ids):
        if (user.pk == other_user.pk):
            return self.model.RANK_0
        if (not (other_user.photo.visible_on_website)):
            return self.model.RANK_0
        if (other_user.gender not in user.speedy_match_profile.gender_to_match):
            return self.model.RANK_0
        if (user.gender not in other_user.speedy_match_profile.gender_to_match):
            return self.model.RANK_0
        if (not (user.speedy_match_profile.min_age_to_match <= other_user.get_age() <= user.speedy_match_profile.max_age_to_match)):
            return self.model.RANK_0
        if (not (other_user.speedy_match_profile.min_age_to_match <= user.get_age() <= other_user.speedy_match_profile.max_age_to_match)):
            return self.model.RANK_0
        if (not ((self.model.settings.MIN_HEIGHT_TO_MATCH <= user.speedy_match_profile.height <= self.model.settings.MAX_HEIGHT_TO_MATCH) and (self.model.settings.MIN_HEIGHT_TO_MATCH <= other_user.speedy_match_profile.height <= self.model.settings.MAX_HEIGHT_TO_MATCH))):
            return self.model.RANK_0
        if (user.speedy_match_profile.not_allowed_to_use_speedy_match or other_user.speedy_match_profile.not_allowed_to_use_speedy_match):
            return self.model.RANK_0
        if (other_user.pk in blocked_users_ids):
            return self.model.RANK_0
        if (other_user.pk in blocking_users_ids):
            return self.model.RANK_0
        other_diet_rank = other_user.speedy_match_profile.diet_match.get(str(user.diet), self.model.RANK_0)
        other_smoking_status_rank = other_user.speedy_match_profile.smoking_status_match.get(str(user.smoking_status), self.model.RANK_0)
        other_relationship_status_rank = other_user.speedy_match_profile.relationship_status_match.get(str(user.relationship_status), self.model.RANK_0)
        other_user_rank = min([other_diet_rank, other_smoking_status_rank, other_relationship_status_rank])
        if (other_user_rank == self.model.RANK_0):
            return self.model.RANK_0
        diet_rank = user.speedy_match_profile.diet_match.get(str(other_user.diet), self.model.RANK_0)
        smoking_status_rank = user.speedy_match_profile.smoking_status_match.get(str(other_user.smoking_status), self.model.RANK_0)
        relationship_status_rank = user.speedy_match_profile.relationship_status_match.get(str(other_user.relationship_status), self.model.RANK_0)
        rank = min([diet_rank, smoking_status_rank, relationship_status_rank])
        return rank

    def get_matches(self, user):
        """
        Get matches from database.

        Checks only first 2,400 users who match this user (sorted by last visit to Speedy Match), and return up to 720 users.
        """
        user.speedy_match_profile._set_values_to_match()
        age_ranges = get_age_ranges_match(min_age=user.speedy_match_profile.min_age_to_match, max_age=user.speedy_match_profile.max_age_to_match)
        language_code = get_language()
        logger.debug("SiteProfileManager::get_matches:start:user={user}, language_code={language_code}".format(
            user=user,
            language_code=language_code,
        ))
        # blocked_users_ids = Block.objects.filter(blocker__pk=user.pk).values_list('blocked_id', flat=True)
        # blocking_users_ids = Block.objects.filter(blocked__pk=user.pk).values_list('blocker_id', flat=True)
        blocked_users_ids = [block.blocked_id for block in user.blocked_entities.all()]
        blocking_users_ids = [block.blocker_id for block in user.blocking_entities.all()]
        qs = User.objects.active(
            photo__visible_on_website=True,
            gender__in=user.speedy_match_profile.gender_to_match,
            diet__in=user.speedy_match_profile.diet_to_match,
            smoking_status__in=user.speedy_match_profile.smoking_status_to_match,
            relationship_status__in=user.speedy_match_profile.relationship_status_to_match,
            speedy_match_site_profile__gender_to_match__contains=[user.gender],
            speedy_match_site_profile__diet_to_match__contains=[user.diet],
            speedy_match_site_profile__smoking_status_to_match__contains=[user.smoking_status],
            speedy_match_site_profile__relationship_status_to_match__contains=[user.relationship_status],
            date_of_birth__range=age_ranges,
            speedy_match_site_profile__min_age_to_match__lte=user.get_age(),
            speedy_match_site_profile__max_age_to_match__gte=user.get_age(),
            speedy_match_site_profile__height__range=(self.model.settings.MIN_HEIGHT_TO_MATCH, self.model.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
        ).exclude(
            pk__in=[user.pk] + blocked_users_ids + blocking_users_ids,
        ).prefetch_related(
            "likes_to_user",
            "friends",
        ).order_by('-speedy_match_site_profile__last_visit')
        user_list = qs[:2400]
        # matches_list = [other_user for other_user in user_list if ((other_user.speedy_match_profile.is_active) and (user.speedy_match_profile.get_matching_rank(other_profile=other_user.speedy_match_profile) > self.model.RANK_0))]
        matches_list = []
        datetime_now = datetime.now()
        timezone_now = now()
        today = date.today()
        for other_user in user_list:
            other_user.speedy_match_profile.rank = self._get_rank(
                user=user,
                other_user=other_user,
                blocked_users_ids=blocked_users_ids,
                blocking_users_ids=blocking_users_ids,
            )
            if ((other_user.speedy_match_profile.is_active) and (other_user.speedy_match_profile.rank > self.model.RANK_0)):
                other_user.speedy_match_profile._likes_to_user_count = len(other_user.likes_to_user.all())
                other_user.speedy_match_profile._friends_count = len(other_user.friends.all())
                other_user.speedy_match_profile._user_last_visit_days_offset = 0 * 30
                if ((timezone_now - other_user.date_created).days < 15) or ((timezone_now - other_user.speedy_match_profile.last_visit).days < 5):
                    other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                else:
                    if (other_user.speedy_match_profile.rank >= self.model.RANK_5) and ((timezone_now - other_user.speedy_match_profile.last_visit).days < 10):
                        other_user.speedy_match_profile._user_last_visit_days_offset += 0
                    else:
                        if (other_user.speedy_match_profile._likes_to_user_count >= 10):
                            other_user.speedy_match_profile._user_last_visit_days_offset += 0
                        elif (other_user.speedy_match_profile._likes_to_user_count >= 3):
                            other_user.speedy_match_profile._user_last_visit_days_offset += 30
                        else:
                            other_user.speedy_match_profile._user_last_visit_days_offset += 80
                    if (other_user.speedy_match_profile.rank >= self.model.RANK_5):
                        other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                    else:
                        if (other_user.speedy_match_profile._friends_count >= 20):
                            other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                        else:
                            other_user.speedy_match_profile._user_last_visit_days_offset += 1 * 30
                        if (other_user.get_age() >= 18):
                            if (120 <= other_user.speedy_match_profile.height <= 235):
                                other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                            else:
                                other_user.speedy_match_profile._user_last_visit_days_offset += 1 * 30
                        else:
                            if (50 <= other_user.speedy_match_profile.height <= 235):
                                other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                            else:
                                other_user.speedy_match_profile._user_last_visit_days_offset += 1 * 30
                if ((timezone_now - other_user.speedy_match_profile.last_visit).days < 10):
                    other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                else:
                    if (other_user.speedy_match_profile.rank >= self.model.RANK_5) and ((timezone_now - other_user.speedy_match_profile.last_visit).days < 20):
                        other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                    else:
                        # Generate a random number which changes every 4 hours, but doesn't change when reloading the page.
                        s = int(hashlib.md5("$$$-{}-{}-{}-{}-{}-$$$".format(other_user.id, today.isoformat(), (((datetime_now.hour // 4) + 1) * 97), (int(other_user.id) % 777), (int(other_user.id) % 458)).encode('utf-8')).hexdigest(), 16) % 12
                        if (s in {0, 4, 8, 10}):  # 4/12
                            other_user.speedy_match_profile._user_last_visit_days_offset += 1 * 30
                        elif (s in {2, 6, 11}):  # 3/12
                            other_user.speedy_match_profile._user_last_visit_days_offset += 2 * 30
                        else:  # 5/12
                            other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                if (other_user.speedy_match_profile.rank >= self.model.RANK_5):
                    other_user.speedy_match_profile._user_last_visit_days_offset -= 1 * 30
                if (other_user.speedy_match_profile._user_last_visit_days_offset < 0):
                    other_user.speedy_match_profile._user_last_visit_days_offset = 0
                profile_description = other_user.speedy_match_profile.profile_description
                profile_description_split = profile_description.split()
                match_description = other_user.speedy_match_profile.match_description
                match_description_split = match_description.split()
                if ((string_is_not_empty(profile_description)) and (len(profile_description) >= 20) and (len(profile_description_split) >= 10)):
                    other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                else:
                    other_user.speedy_match_profile._user_last_visit_days_offset += 3 * 30
                if ((string_is_not_empty(match_description)) and (len(match_description) >= 20) and (len(match_description_split) >= 8)):
                    other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                else:
                    other_user.speedy_match_profile._user_last_visit_days_offset += 1 * 30
                if ((string_is_not_empty(profile_description)) and (len(profile_description_split) > 0) and (len(profile_description_split) / len(set(profile_description_split)) < 2.5)):
                    other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                else:
                    other_user.speedy_match_profile._user_last_visit_days_offset += 20 * 30
                if ((string_is_not_empty(match_description)) and (len(match_description_split) > 0) and (len(match_description_split) / len(set(match_description_split)) < 2.5)):
                    other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                else:
                    other_user.speedy_match_profile._user_last_visit_days_offset += 20 * 30
                other_user.speedy_match_profile._user_last_visit_days_offset += other_user.speedy_match_profile.profile_picture_months_offset * 30
                # Generate a random number which changes every 4 hours, but doesn't change when reloading the page.
                s = int(hashlib.md5("$$$-{}-{}-{}-{}-{}-$$$".format(other_user.id, today.isoformat(), (((datetime_now.hour // 4) + 1) * 98), (int(other_user.id) % 777), (int(other_user.id) % 458)).encode('utf-8')).hexdigest(), 16) % 77
                if (s in {24, 48, 72}):  # 3/77
                    other_user.speedy_match_profile._user_last_visit_days_offset -= 6 * 30
                elif (s in {25, 49, 73}):  # 3/77
                    other_user.speedy_match_profile._user_last_visit_days_offset -= 2 * 30
                else:  # 71/77
                    if ((timezone_now - other_user.speedy_match_profile.last_visit).days < 5):
                        other_user.speedy_match_profile._user_last_visit_days_offset -= 0 * 30
                    else:
                        if (s in {27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 50, 51}):  # 23/77
                            other_user.speedy_match_profile._user_last_visit_days_offset += 1 * 30
                        elif (s in {52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 74, 75, 76}):  # 23/77
                            other_user.speedy_match_profile._user_last_visit_days_offset += 2 * 30
                        else:  # 25/77
                            other_user.speedy_match_profile._user_last_visit_days_offset -= 0 * 30
                matches_list.append(other_user)
        if (not (len(matches_list) == len(user_list))):
            # This is an error. All users should have ranks more than 0.
            logger.error('SiteProfileManager::get_matches:get inside "if (not (len(matches_list) == len(user_list))):", user={user}, language_code={language_code}, number_of_users={number_of_users}, number_of_matches={number_of_matches}'.format(
                user=user,
                language_code=language_code,
                number_of_users=len(user_list),
                number_of_matches=len(matches_list),
            ))
        matches_list = sorted(matches_list, key=lambda u: (-(max([((timezone_now - u.speedy_match_profile.last_visit).days + u.speedy_match_profile._user_last_visit_days_offset), 0]) // 40), u.speedy_match_profile.rank, u.speedy_match_profile.last_visit), reverse=True)
        matches_list = matches_list[:720]
        # Save number of matches in this language in user's profile.
        user.speedy_match_profile.number_of_matches = len(matches_list)
        user.speedy_match_profile.save()
        logger.debug("SiteProfileManager::get_matches:end:user={user}, language_code={language_code}, number_of_users={number_of_users}, number_of_matches={number_of_matches}".format(
            user=user,
            language_code=language_code,
            number_of_users=len(user_list),
            number_of_matches=len(matches_list),
        ))
        if ((not (self.model.settings.MIN_HEIGHT_TO_MATCH <= user.speedy_match_profile.height <= self.model.settings.MAX_HEIGHT_TO_MATCH)) or (user.speedy_match_profile.height <= 85) or (user.speedy_match_profile.not_allowed_to_use_speedy_match)):
            logger.warning("SiteProfileManager::get_matches:user={user}, language_code={language_code}, number_of_users={number_of_users}, number_of_matches={number_of_matches}, height={height}, not_allowed_to_use_speedy_match={not_allowed_to_use_speedy_match}".format(
                user=user,
                language_code=language_code,
                number_of_users=len(user_list),
                number_of_matches=len(matches_list),
                height=user.speedy_match_profile.height,
                not_allowed_to_use_speedy_match=user.speedy_match_profile.not_allowed_to_use_speedy_match,
            ))
        return matches_list

    def get_matches_from_list(self, user, from_list):
        user.speedy_match_profile._set_values_to_match()
        age_ranges = get_age_ranges_match(min_age=user.speedy_match_profile.min_age_to_match, max_age=user.speedy_match_profile.max_age_to_match)
        language_code = get_language()
        logger.debug("SiteProfileManager::get_matches_from_list:start:user={user}, language_code={language_code}".format(
            user=user,
            language_code=language_code,
        ))
        # blocked_users_ids = Block.objects.filter(blocker__pk=user.pk).values_list('blocked_id', flat=True)
        # blocking_users_ids = Block.objects.filter(blocked__pk=user.pk).values_list('blocker_id', flat=True)
        blocked_users_ids = [block.blocked_id for block in user.blocked_entities.all()]
        blocking_users_ids = [block.blocker_id for block in user.blocking_entities.all()]
        qs = User.objects.active(
            pk__in=from_list,
            photo__visible_on_website=True,
            gender__in=user.speedy_match_profile.gender_to_match,
            diet__in=user.speedy_match_profile.diet_to_match,
            smoking_status__in=user.speedy_match_profile.smoking_status_to_match,
            relationship_status__in=user.speedy_match_profile.relationship_status_to_match,
            speedy_match_site_profile__gender_to_match__contains=[user.gender],
            speedy_match_site_profile__diet_to_match__contains=[user.diet],
            speedy_match_site_profile__smoking_status_to_match__contains=[user.smoking_status],
            speedy_match_site_profile__relationship_status_to_match__contains=[user.relationship_status],
            date_of_birth__range=age_ranges,
            speedy_match_site_profile__min_age_to_match__lte=user.get_age(),
            speedy_match_site_profile__max_age_to_match__gte=user.get_age(),
            speedy_match_site_profile__height__range=(self.model.settings.MIN_HEIGHT_TO_MATCH, self.model.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
        ).exclude(
            pk__in=[user.pk] + blocked_users_ids + blocking_users_ids,
        ).order_by('-speedy_match_site_profile__last_visit')
        user_list = qs
        # matches_list = [other_user for other_user in user_list if ((other_user.speedy_match_profile.is_active) and (user.speedy_match_profile.get_matching_rank(other_profile=other_user.speedy_match_profile) > self.model.RANK_0))]
        matches_list = []
        timezone_now = now()
        for other_user in user_list:
            other_user.speedy_match_profile.rank = self._get_rank(
                user=user,
                other_user=other_user,
                blocked_users_ids=blocked_users_ids,
                blocking_users_ids=blocking_users_ids,
            )
            if ((other_user.speedy_match_profile.is_active) and (other_user.speedy_match_profile.rank > self.model.RANK_0)):
                matches_list.append(other_user)
        if (not (len(matches_list) == len(user_list))):
            # This is an error. All users should have ranks more than 0.
            logger.error('SiteProfileManager::get_matches_from_list:get inside "if (not (len(matches_list) == len(user_list))):", user={user}, language_code={language_code}, from_list_len={from_list_len}, number_of_users={number_of_users}, number_of_matches={number_of_matches}'.format(
                user=user,
                language_code=language_code,
                from_list_len=len(from_list),
                number_of_users=len(user_list),
                number_of_matches=len(matches_list),
            ))
        matches_list = sorted(matches_list, key=lambda u: (-((timezone_now - u.speedy_match_profile.last_visit).days // 40), u.speedy_match_profile.rank, u.speedy_match_profile.last_visit), reverse=True)
        logger.debug("SiteProfileManager::get_matches_from_list:end:user={user}, language_code={language_code}, from_list_len={from_list_len}, number_of_users={number_of_users}, number_of_matches={number_of_matches}".format(
            user=user,
            language_code=language_code,
            from_list_len=len(from_list),
            number_of_users=len(user_list),
            number_of_matches=len(matches_list),
        ))
        return matches_list


