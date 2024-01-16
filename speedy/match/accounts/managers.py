import logging
import hashlib
import random
from datetime import timedelta, datetime, date
from haversine import haversine, Unit

from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db import models
from django.dispatch import receiver
from django.utils.timezone import now
from django.utils.translation import get_language

from speedy.core.base import cache_manager
from speedy.core.base.utils import get_age_ranges_match, string_is_not_empty
from speedy.core.base.managers import BaseManager
from speedy.core.accounts.models import User

logger = logging.getLogger(__name__)

CACHE_TYPES = {
    'matches': 'speedy-m-%s',
}

BUST_CACHES = {
    'matches': ['matches'],
}


def cache_key(type, entity_pk):
    return CACHE_TYPES[type] % entity_pk


def bust_cache(type, entity_pk, version=None):
    bust_keys = BUST_CACHES[type]
    keys = [cache_key(type=k, entity_pk=entity_pk) for k in bust_keys]
    cache_manager.cache_delete_many(keys=keys, version=version)


@receiver(signal=models.signals.post_save, sender=User)
def invalidate_matches_after_update_user(sender, instance: User, **kwargs):
    if (not (getattr(instance.profile, '_in_update_last_visit', None))):
        bust_cache(type='matches', entity_pk=instance.pk)


class SiteProfileManager(BaseManager):
    def _get_rank(self, user, other_user, blocked_users_ids, blocking_users_ids):
        """
        Same function as user.speedy_match_profile.get_matching_rank(other_profile=other_user.speedy_match_profile), but more optimized.

        :param user:
        :param other_user:
        :param blocked_users_ids: The IDs of the users who this user blocked.
        :param blocking_users_ids: The IDs of the users who blocked this user.
        :return: The rank of the other user.
        """
        if (user.pk == other_user.pk):
            return self.model.RANK_0
        if ((not (user.speedy_match_profile.is_active)) or (not (other_user.speedy_match_profile.is_active))):
            return self.model.RANK_0
        if (user.speedy_match_profile.not_allowed_to_use_speedy_match or other_user.speedy_match_profile.not_allowed_to_use_speedy_match):
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

    def _get_distance_offset(self, index):
        """
        Get distance offset for a given index.

        :param index: must be in {0, 2, 4, 6, 8, 10}.
        :return: distance offset (in days).
        """
        if (not (index in {0, 2, 4, 6, 8, 10})):
            logger.warning("SiteProfileManager::_get_distance_offset:index is invalid! index={index}".format(
                index=index,
            ))
        if (index < 10):
            distance_offset = int(index / 10 * 8 * 30 + 0.5)
        else:
            distance_offset = int(index / 10 * 15 * 30 + 0.5)
        return distance_offset

    def _get_matching_users_queryset(self, user, from_list=None):
        """
        Get matching users queryset.

        :param user:
        :param from_list: A given list of users (optional).
        :return: Queryset of matching users.
        """
        user.speedy_match_profile._set_values_to_match()
        age_ranges = get_age_ranges_match(min_age=user.speedy_match_profile.min_age_to_match, max_age=user.speedy_match_profile.max_age_to_match)
        language_code = get_language()
        blocked_users_ids = user.blocked_entities_ids
        blocking_users_ids = user.blocking_entities_ids
        filter_dict = dict(
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
        )
        if (from_list is not None):
            filter_dict["pk__in"] = from_list
        qs = User.objects.active(
            **filter_dict
        ).exclude(
            pk__in=[user.pk] + blocked_users_ids + blocking_users_ids,
        ).order_by('-speedy_match_site_profile__last_visit')
        return qs

    def _get_matches(self, user):
        """
        Get matches from database.

        Checks only first 2,400 users who match this user (sorted by last visit to Speedy Match), and return up to 720 users.

        :param user:
        :return: Up to 720 matching users.
        """
        language_code = get_language()
        logger.debug("SiteProfileManager::_get_matches:start:user={user}, language_code={language_code}".format(
            user=user,
            language_code=language_code,
        ))
        datetime_now = datetime.now()
        timezone_now = now()
        today = date.today()
        blocked_users_ids = user.blocked_entities_ids
        blocking_users_ids = user.blocking_entities_ids
        qs = self._get_matching_users_queryset(user=user)
        _user_list = qs[:2400]
        # If there are at least 1,080 users who visited Speedy Match in the last 4 months, use them. Otherwise check 8 months, 12 months etc.
        user_list = []
        months = None
        for m in range(4, 28, 4):
            if (months is None):
                user_list = [u for u in _user_list if ((timezone_now - u.speedy_match_profile.last_visit).days <= m * 30)]
                if ((m == 24) or (len(user_list) >= 1080)):
                    months = m
        matches_list = []
        for other_user in user_list:
            other_user.speedy_match_profile.rank = self._get_rank(
                user=user,
                other_user=other_user,
                blocked_users_ids=blocked_users_ids,
                blocking_users_ids=blocking_users_ids,
            )
            if ((user.speedy_match_profile.is_active) and (other_user.speedy_match_profile.is_active) and (other_user.speedy_match_profile.rank > self.model.RANK_0)):
                other_user.speedy_match_profile._likes_to_user_count = other_user.speedy_match_profile.likes_to_user_count
                other_user.speedy_match_profile._friends_count = other_user.speedy_net_profile.friends_count
                other_user.speedy_match_profile._distance_between_users = None
                other_user.speedy_match_profile._user_last_visit_days_offset = 0 * 30
                if ((timezone_now - other_user.speedy_match_profile.last_visit).days >= 180):
                    other_user.speedy_match_profile._user_last_visit_days_offset += 6 * 30
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
                        s = int(hashlib.md5("$$$-{}-{}-{}-{}-{}-$$$".format(user.id, other_user.id, today.isoformat(), (datetime_now.hour // 4), "97-97a").encode('utf-8')).hexdigest(), 16) % 12
                        if (5 <= s < 9):  # 4/12
                            other_user.speedy_match_profile._user_last_visit_days_offset += 1 * 30
                        elif (9 <= s < 12):  # 3/12
                            other_user.speedy_match_profile._user_last_visit_days_offset += 2 * 30
                        else:  # 5/12
                            other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                # Generate a random number which changes every 4 hours, but doesn't change when reloading the page.
                s = int(hashlib.md5("$$$-{}-{}-{}-{}-{}-$$$".format(user.id, other_user.id, today.isoformat(), (datetime_now.hour // 4), "92-92a").encode('utf-8')).hexdigest(), 16) % 6000
                if (0 <= s < 480):  # 480/6000
                    if (0 <= s < 36):  # 36/6000
                        index = (s % 3) * 2
                    else:  # 444/6000
                        index = (s % 3 + 3) * 2
                    distance_offset = self._get_distance_offset(index=index)
                    if (index == 0):
                        other_user.speedy_match_profile._distance_between_users = "30.0 distance_offset #1"
                    elif (index == 2):
                        other_user.speedy_match_profile._distance_between_users = "180.0 distance_offset #1"
                    elif (index == 4):
                        other_user.speedy_match_profile._distance_between_users = "750.0 distance_offset #1"
                    elif (index == 6):
                        other_user.speedy_match_profile._distance_between_users = "2100.0 distance_offset #1"
                    elif (index == 8):
                        other_user.speedy_match_profile._distance_between_users = "4500.0 distance_offset #1"
                    elif (index == 10):
                        other_user.speedy_match_profile._distance_between_users = "12000.0 distance_offset #1"
                    if (random.randint(0, 7999) == 0):
                        logger.debug("SiteProfileManager::_get_matches:distance_offset #1: {user} and {other_user}, s is {s}, distance offset is {distance_offset} .".format(
                            user=user,
                            other_user=other_user,
                            s=s,
                            distance_offset=distance_offset,
                        ))
                else:
                    distance_offset = self._get_distance_offset(index=10)
                    try:
                        if ((user.last_ip_address_used_raw_ipapi_results is not None) and (other_user.last_ip_address_used_raw_ipapi_results is not None)):
                            if (
                                ("latitude" in user.last_ip_address_used_raw_ipapi_results) and
                                (user.last_ip_address_used_raw_ipapi_results["latitude"] is not None) and
                                ("longitude" in user.last_ip_address_used_raw_ipapi_results) and
                                (user.last_ip_address_used_raw_ipapi_results["longitude"] is not None) and
                                ("latitude" in other_user.last_ip_address_used_raw_ipapi_results) and
                                (other_user.last_ip_address_used_raw_ipapi_results["latitude"] is not None) and
                                ("longitude" in other_user.last_ip_address_used_raw_ipapi_results) and
                                (other_user.last_ip_address_used_raw_ipapi_results["longitude"] is not None)
                            ):
                                user_latitude = float(user.last_ip_address_used_raw_ipapi_results["latitude"])
                                user_longitude = float(user.last_ip_address_used_raw_ipapi_results["longitude"])
                                other_user_latitude = float(other_user.last_ip_address_used_raw_ipapi_results["latitude"])
                                other_user_longitude = float(other_user.last_ip_address_used_raw_ipapi_results["longitude"])
                                distance_between_users = haversine(point1=(user_latitude, user_longitude), point2=(other_user_latitude, other_user_longitude), unit=Unit.KILOMETERS)
                                if (distance_between_users < 60):
                                    distance_offset = self._get_distance_offset(index=0)
                                elif (distance_between_users < 300):
                                    distance_offset = self._get_distance_offset(index=2)
                                elif (distance_between_users < 1200):
                                    distance_offset = self._get_distance_offset(index=4)
                                elif (distance_between_users < 3000):
                                    distance_offset = self._get_distance_offset(index=6)
                                elif (distance_between_users < 6000):
                                    distance_offset = self._get_distance_offset(index=8)
                                else:
                                    distance_offset = self._get_distance_offset(index=10)
                                other_user.speedy_match_profile._distance_between_users = distance_between_users
                                if (random.randint(0, 7999) == 0):
                                    logger.debug("SiteProfileManager::_get_matches:distance_offset #2:s is {s}, distance offset is {distance_offset}, The distance between {user} and {other_user} is {distance_between_users} km.".format(
                                        user=user,
                                        other_user=other_user,
                                        distance_between_users=distance_between_users,
                                        s=s,
                                        distance_offset=distance_offset,
                                    ))
                    except Exception as e:
                        logger.debug("SiteProfileManager::_get_matches:Can't calculate distance between users, user={user}, other_user={other_user}, Exception={e} (registered {registered_days_ago} days ago)".format(
                            user=user,
                            other_user=other_user,
                            e=str(e),
                            registered_days_ago=(now() - user.date_created).days,
                        ))
                        distance_offset = self._get_distance_offset(index=10)
                other_user.speedy_match_profile._user_last_visit_days_offset += distance_offset
                if (other_user.speedy_match_profile.rank >= self.model.RANK_5):
                    other_user.speedy_match_profile._user_last_visit_days_offset -= 1 * 30
                if (other_user.speedy_match_profile._user_last_visit_days_offset < 0):
                    other_user.speedy_match_profile._user_last_visit_days_offset = 0
                profile_description = other_user.speedy_match_profile.profile_description
                if (string_is_not_empty(profile_description)):
                    profile_description_split = profile_description.split()
                else:
                    profile_description_split = "".split()
                match_description = other_user.speedy_match_profile.match_description
                if (string_is_not_empty(match_description)):
                    match_description_split = match_description.split()
                else:
                    match_description_split = "".split()
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
                s = int(hashlib.md5("$$$-{}-{}-{}-{}-{}-$$$".format(user.id, other_user.id, today.isoformat(), (datetime_now.hour // 4), "98-98a").encode('utf-8')).hexdigest(), 16) % 77
                if (74 <= s < 77):  # 3/77
                    other_user.speedy_match_profile._user_last_visit_days_offset -= 6 * 30
                elif (71 <= s < 74):  # 3/77
                    other_user.speedy_match_profile._user_last_visit_days_offset -= 2 * 30
                else:  # 71/77
                    if ((timezone_now - other_user.speedy_match_profile.last_visit).days < 5):
                        other_user.speedy_match_profile._user_last_visit_days_offset -= 0 * 30
                    else:
                        if (48 <= s < 71):  # 23/77
                            other_user.speedy_match_profile._user_last_visit_days_offset += 1 * 30
                        elif (25 <= s < 48):  # 23/77
                            other_user.speedy_match_profile._user_last_visit_days_offset += 2 * 30
                        else:  # 25/77
                            other_user.speedy_match_profile._user_last_visit_days_offset -= 0 * 30
                matches_list.append(other_user)
        if (not (len(matches_list) == len(user_list))):
            if (((not (user.speedy_match_profile.is_active)) or (user.speedy_match_profile.not_allowed_to_use_speedy_match)) and (len(matches_list) == 0)):
                pass
            else:
                # This is an error. All users should have ranks more than 0.
                logger.error('SiteProfileManager::_get_matches:get inside "if (not (len(matches_list) == len(user_list))):", user={user}, language_code={language_code}, number_of_users={number_of_users}, number_of_matches={number_of_matches}'.format(
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
        logger.debug("SiteProfileManager::_get_matches:end:user={user}, language_code={language_code}, months={months}, number_of_users={number_of_users}, number_of_matches={number_of_matches}, user_id_list={user_id_list}, distance_between_users_list={distance_between_users_list}".format(
            user=user,
            language_code=language_code,
            months=months,
            number_of_users=len(user_list),
            number_of_matches=len(matches_list),
            user_id_list=[u.id for u in matches_list[:40]],
            distance_between_users_list=[getattr(u.speedy_match_profile, "_distance_between_users", None) for u in matches_list[:40]],
        ))
        if ((not (self.model.settings.MIN_HEIGHT_TO_MATCH <= user.speedy_match_profile.height <= self.model.settings.MAX_HEIGHT_TO_MATCH)) or (user.speedy_match_profile.height <= 85) or (user.speedy_match_profile.not_allowed_to_use_speedy_match)):
            logger.warning("SiteProfileManager::_get_matches:user={user}, language_code={language_code}, number_of_users={number_of_users}, number_of_matches={number_of_matches}, height={height}, not_allowed_to_use_speedy_match={not_allowed_to_use_speedy_match}".format(
                user=user,
                language_code=language_code,
                number_of_users=len(user_list),
                number_of_matches=len(matches_list),
                height=user.speedy_match_profile.height,
                not_allowed_to_use_speedy_match=user.speedy_match_profile.not_allowed_to_use_speedy_match,
            ))
        return matches_list

    def get_matches_from_list(self, user, from_list):
        """
        Get matches from database, from a given list of users.

        :param user:
        :param from_list: A given list of users.
        :return: matching users.
        """
        language_code = get_language()
        # Log this function only 0.2% of the time, since it's called very often.
        log_this_function = (random.randint(0, 499) == 0)
        if (log_this_function):
            logger.debug("SiteProfileManager::get_matches_from_list:start:user={user}, language_code={language_code}".format(
                user=user,
                language_code=language_code,
            ))
        timezone_now = now()
        blocked_users_ids = user.blocked_entities_ids
        blocking_users_ids = user.blocking_entities_ids
        qs = self._get_matching_users_queryset(user=user, from_list=from_list)
        user_list = qs
        matches_list = []
        for other_user in user_list:
            other_user.speedy_match_profile.rank = self._get_rank(
                user=user,
                other_user=other_user,
                blocked_users_ids=blocked_users_ids,
                blocking_users_ids=blocking_users_ids,
            )
            if ((user.speedy_match_profile.is_active) and (other_user.speedy_match_profile.is_active) and (other_user.speedy_match_profile.rank > self.model.RANK_0)):
                matches_list.append(other_user)
        if (not (len(matches_list) == len(user_list))):
            if (((not (user.speedy_match_profile.is_active)) or (user.speedy_match_profile.not_allowed_to_use_speedy_match)) and (len(matches_list) == 0)):
                pass
            else:
                # This is an error. All users should have ranks more than 0.
                logger.error('SiteProfileManager::get_matches_from_list:get inside "if (not (len(matches_list) == len(user_list))):", user={user}, language_code={language_code}, from_list_len={from_list_len}, number_of_users={number_of_users}, number_of_matches={number_of_matches}'.format(
                    user=user,
                    language_code=language_code,
                    from_list_len=len(from_list),
                    number_of_users=len(user_list),
                    number_of_matches=len(matches_list),
                ))
        matches_list = sorted(matches_list, key=lambda u: (-((timezone_now - u.speedy_match_profile.last_visit).days // 40), u.speedy_match_profile.rank, u.speedy_match_profile.last_visit), reverse=True)
        if (log_this_function):
            logger.debug("SiteProfileManager::get_matches_from_list:end:user={user}, language_code={language_code}, from_list_len={from_list_len}, number_of_users={number_of_users}, number_of_matches={number_of_matches}".format(
                user=user,
                language_code=language_code,
                from_list_len=len(from_list),
                number_of_users=len(user_list),
                number_of_matches=len(matches_list),
            ))
        return matches_list

    def get_matches(self, user):
        """
        Get matches from database.

        Checks only first 2,400 users who match this user (sorted by last visit to Speedy Match), and return up to 720 users.

        :param user:
        :return: Up to 720 matching users.
        """
        language_code = get_language()
        logger.debug("SiteProfileManager::get_matches:start:user={user}, language_code={language_code}".format(
            user=user,
            language_code=language_code,
        ))
        matches_key = cache_key(type='matches', entity_pk=user.pk)
        matches_users_ids = cache_manager.cache_get(key=matches_key, sliding_timeout=DEFAULT_TIMEOUT)
        if (matches_users_ids is not None):
            from_cache = "yes"
            matches_list = self.get_matches_from_list(user=user, from_list=matches_users_ids)
            matches_order = {u: i for i, u in enumerate(matches_users_ids)}
            matches_list = sorted(matches_list, key=lambda u: matches_order[u.id])
        else:
            from_cache = "no"
            matches_list = self._get_matches(user=user)
            matches_users_ids = [u.id for u in matches_list]
            cache_manager.cache_set(key=matches_key, value=matches_users_ids)
        logger.debug("SiteProfileManager::get_matches:end:user={user}, language_code={language_code}, number_of_matches={number_of_matches}, from_cache={from_cache}".format(
            user=user,
            language_code=language_code,
            number_of_matches=len(matches_list),
            from_cache=from_cache,
        ))
        return matches_list


