from django.db.models import Q
from django.conf import settings

from rules import predicate, add_perm, remove_perm, always_allow

from speedy.core.accounts.base_rules import is_self
from speedy.core.accounts.rules import has_access_perm
from speedy.core.blocks.rules import is_blocked, there_is_block
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
from speedy.core.im.models import Chat
from speedy.core.blocks.models import Block
from speedy.match.likes.models import UserLike


@predicate
def is_match_profile(user, other_user):
    if (user.is_authenticated):
        match_profile = user.speedy_match_profile.get_matching_rank(other_profile=other_user.speedy_match_profile) > SpeedyMatchSiteProfile.RANK_0
        has_message = Chat.on_site.filter((Q(ent1_id=user) & Q(ent2_id=other_user)) | (Q(ent1_id=other_user) & Q(ent2_id=user))).exists()
        has_likes = UserLike.objects.filter((Q(from_user=user) & Q(to_user=other_user)) | (Q(from_user=other_user) & Q(to_user=user))).exists()
        has_blocked = Block.objects.has_blocked(blocker=user, blocked=other_user)
        return (is_self(user=user, other_user=other_user)) or (match_profile or has_message or has_likes or has_blocked)
    return False


if (settings.SITE_ID == settings.SPEEDY_MATCH_SITE_ID):
    remove_perm('accounts.view_profile')
    add_perm('accounts.view_profile', has_access_perm & ~there_is_block & is_match_profile)
    remove_perm('accounts.view_profile_header')
    add_perm('accounts.view_profile_header', has_access_perm & ~is_blocked & is_match_profile)
    remove_perm('accounts.view_profile_info')
    add_perm('accounts.view_profile_info', has_access_perm & ~is_blocked & is_match_profile)
    remove_perm('accounts.view_profile_age')
    add_perm('accounts.view_profile_age', always_allow)


