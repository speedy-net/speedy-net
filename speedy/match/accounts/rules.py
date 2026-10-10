from django.db.models import Q
from django.conf import settings as django_settings

from rules import predicate, add_perm, always_allow, always_deny

from speedy.core.accounts.base_rules import is_self, is_active
from speedy.core.accounts.rules import has_access_perm
from speedy.core.blocks.rules import is_blocked, there_is_block
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
from speedy.core.messages.models import Chat
from speedy.core.blocks.models import Block
from speedy.match.likes.models import UserLike


@predicate
def is_match_profile(user, other_user):
    """
    Checks whether the user has a visible profile relation to another user on Speedy Match - either they are the same user, a match, have exchanged messages or likes, or one has blocked the other, and both are active (or the viewer is a staff superuser).

    :param user: The user requesting access.
    :type user: speedy.core.accounts.models.User
    :param other_user: The user whose profile is being accessed.
    :type other_user: speedy.core.accounts.models.User
    :return: True if the profile relation grants access, False otherwise.
    :rtype: bool
    """
    if (user.is_authenticated):
        if ((user.is_staff) and (user.is_superuser)):
            return True
        match_profile = (user.speedy_match_profile.get_matching_rank(other_profile=other_user.speedy_match_profile) > SpeedyMatchSiteProfile.RANK_0)
        has_message = Chat.objects.filter((Q(ent1_id=user) & Q(ent2_id=other_user)) | (Q(ent1_id=other_user) & Q(ent2_id=user))).exists()
        has_likes = UserLike.objects.filter((Q(from_user=user) & Q(to_user=other_user)) | (Q(from_user=other_user) & Q(to_user=user))).exists()
        has_blocked = Block.objects.has_blocked(blocker=user, blocked=other_user)
        return (is_self(user=user, other_user=other_user)) or ((is_active(user=user, other_user=other_user)) and (match_profile or has_message or has_likes or has_blocked))
    return False


if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
    add_perm(name='accounts.view_profile', pred=has_access_perm & ~there_is_block & is_match_profile)
    add_perm(name='accounts.view_profile_header', pred=has_access_perm & ~is_blocked & is_match_profile)
    add_perm(name='accounts.view_profile_info', pred=has_access_perm & ~is_blocked & is_match_profile)
    add_perm(name='accounts.view_profile_age', pred=always_allow)
    add_perm(name='accounts.view_profile_rank', pred=has_access_perm & ~there_is_block & is_match_profile & ~is_self)
    add_perm(name='accounts.view_user_on_speedy_net_widget', pred=has_access_perm & ~there_is_block & is_match_profile)
    add_perm(name='accounts.view_user_on_speedy_match_widget', pred=always_deny)


