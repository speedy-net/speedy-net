from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from speedy.core.base.managers import BaseManager
from speedy.core.accounts.utils import get_site_profile_model
from speedy.core.accounts.models import User


class UserLikeManager(BaseManager):
    """
    Manager for the UserLike model, providing methods for creating/removing likes and for querying like lists (sent, received, mutual).

    Methods:
        add_like(self, from_user, to_user): Creates a like from one user to another, validating it is allowed.
        remove_like(self, from_user, to_user): Removes the like from one user to another, if it exists.
        remove_all_likes_from_user(self, from_user): Removes all likes given by a user.
        remove_all_likes_to_user(self, to_user): Removes all likes received by a user.
        get_like_list_to_queryset(self, user): Returns the queryset of likes given by a user to other active users.
        get_like_list_from_queryset(self, user): Returns the queryset of likes received by a user from other active, non-blocked users.
        get_like_list_mutual_queryset(self, user): Returns the queryset of mutual likes (users who like the given user back).
    """
    def add_like(self, from_user, to_user):
        """
        Creates a like from one user to another, after validating that the users are different, the like doesn't already exist, and there is no block between them.

        :param from_user: The user giving the like.
        :type from_user: speedy.core.accounts.models.User
        :param to_user: The user receiving the like.
        :type to_user: speedy.core.accounts.models.User
        :raises django.core.exceptions.ValidationError: If the users are the same, the like already exists, or a block exists between them.
        """
        from speedy.core.blocks.models import Block

        if (from_user == to_user):
            raise ValidationError(_("Users cannot like themselves."))

        if (self.filter(from_user=from_user, to_user=to_user).exists()):
            raise ValidationError(_("User already likes other user."))

        if (Block.objects.there_is_block(entity_1=from_user, entity_2=to_user)):
            raise ValidationError(_("User cannot like a blocked user."))

        self.create(from_user=from_user, to_user=to_user)

    def remove_like(self, from_user, to_user):
        """
        Removes the like from one user to another, if it exists.

        :param from_user: The user who gave the like.
        :type from_user: speedy.core.accounts.models.User
        :param to_user: The user who received the like.
        :type to_user: speedy.core.accounts.models.User
        """
        for like in self.filter(from_user=from_user, to_user=to_user):
            like.delete()

    def remove_all_likes_from_user(self, from_user):
        """
        Removes all likes given by a user.

        :param from_user: The user whose given likes should be removed.
        :type from_user: speedy.core.accounts.models.User
        """
        for like in self.filter(from_user=from_user):
            like.delete()

    def remove_all_likes_to_user(self, to_user):
        """
        Removes all likes received by a user.

        :param to_user: The user whose received likes should be removed.
        :type to_user: speedy.core.accounts.models.User
        """
        for like in self.filter(to_user=to_user):
            like.delete()

    def get_like_list_to_queryset(self, user):
        """
        Returns the queryset of likes given by the user to other users who are still active on Speedy Match.

        :param user: The user whose given likes should be returned.
        :type user: speedy.core.accounts.models.User
        :return: The queryset of UserLike instances given by the user, ordered by the liked user's last visit.
        :rtype: django.db.models.QuerySet
        """
        from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

        SiteProfile = get_site_profile_model()

        # Filter out users that are only active in another language.
        liked_users = User.objects.filter(pk__in=self.filter(from_user=user).values_list('to_user_id', flat=True))
        liked_users = [u.pk for u in liked_users if (u.speedy_match_profile.is_active)]

        return self.filter(from_user=user).filter(to_user__in=liked_users).prefetch_related("to_user", "to_user__{}".format(SpeedyNetSiteProfile.RELATED_NAME), "to_user__{}".format(SpeedyMatchSiteProfile.RELATED_NAME), 'to_user__photo').distinct().order_by('-to_user__{}__last_visit'.format(SiteProfile.RELATED_NAME))

    def get_like_list_from_queryset(self, user):
        """
        Returns the queryset of likes received by the user from other active, non-blocked users.

        :param user: The user whose received likes should be returned.
        :type user: speedy.core.accounts.models.User
        :return: The queryset of UserLike instances received by the user, ordered by the liking user's last visit.
        :rtype: django.db.models.QuerySet
        """
        from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

        SiteProfile = get_site_profile_model()

        # Filter out users that are only active in another language.
        who_likes_me = User.objects.filter(pk__in=self.filter(to_user=user).values_list('from_user_id', flat=True))
        who_likes_me = [u.pk for u in who_likes_me if (u.speedy_match_profile.is_active)]

        # Filter out users I blocked.
        blocked_users_ids = user.blocked_entities_ids
        who_likes_me = [pk for pk in who_likes_me if (not (pk in blocked_users_ids))]

        return self.filter(to_user=user).filter(from_user__in=who_likes_me).prefetch_related("from_user", "from_user__{}".format(SpeedyNetSiteProfile.RELATED_NAME), "from_user__{}".format(SpeedyMatchSiteProfile.RELATED_NAME), 'from_user__photo').distinct().order_by('-from_user__{}__last_visit'.format(SiteProfile.RELATED_NAME))

    def get_like_list_mutual_queryset(self, user):
        """
        Returns the queryset of mutual likes - users the given user likes who also like them back.

        :param user: The user whose mutual likes should be returned.
        :type user: speedy.core.accounts.models.User
        :return: The queryset of UserLike instances representing mutual likes, ordered by the other user's last visit.
        :rtype: django.db.models.QuerySet
        """
        from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

        SiteProfile = get_site_profile_model()

        # Filter out users that are only active in another language.
        who_likes_me = User.objects.filter(pk__in=self.filter(to_user=user).values_list('from_user_id', flat=True))
        who_likes_me = [u.pk for u in who_likes_me if (u.speedy_match_profile.is_active)]

        return self.filter(from_user=user, to_user_id__in=who_likes_me).prefetch_related("to_user", "to_user__{}".format(SpeedyNetSiteProfile.RELATED_NAME), "to_user__{}".format(SpeedyMatchSiteProfile.RELATED_NAME), 'to_user__photo').distinct().order_by('-to_user__{}__last_visit'.format(SiteProfile.RELATED_NAME))


