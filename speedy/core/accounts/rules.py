from django.conf import settings as django_settings

from rules import predicate, add_perm, always_deny

from speedy.core.accounts.base_rules import is_self, is_active
from speedy.core.friends.rules import are_friends
from speedy.core.blocks.rules import there_is_block
from .fields import UserAccessField
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


def _has_access_perm_for_obj(user, other_user, access):
    if (access == UserAccessField.ACCESS_ANYONE):
        return True
    if (user.is_authenticated):
        if (access == UserAccessField.ACCESS_ME):
            return is_self(user=user, other_user=other_user)
        if (access == UserAccessField.ACCESS_FRIENDS):
            return ((is_self(user=user, other_user=other_user)) or (are_friends(user=user, other_user=other_user)))
        if (access == UserAccessField.ACCESS_FRIENDS_AND_FRIENDS_OF_FRIENDS):
            return ((is_self(user=user, other_user=other_user)) or (are_friends(user=user, other_user=other_user)))
    return False


@predicate
def has_access_perm(user, other_user):
    if (user.is_authenticated):
        if ((user.is_staff) and (user.is_superuser)):
            return True
    return is_active(user=user, other_user=other_user)


@predicate
def has_access_perm_for_dob_day_month(user, other_user):
    return _has_access_perm_for_obj(user=user, other_user=other_user, access=other_user.access_dob_day_month)


@predicate
def has_access_perm_for_dob_year(user, other_user):
    return _has_access_perm_for_obj(user=user, other_user=other_user, access=other_user.access_dob_year)


@predicate
def view_user_on_speedy_match_widget(user, other_user):
    if (user.is_authenticated):
        if ((user.is_staff) and (user.is_superuser)):
            return True
        match_profile = (user.speedy_match_profile.get_matching_rank(other_profile=other_user.speedy_match_profile) > SpeedyMatchSiteProfile.RANK_0)
        return match_profile
    return False


@predicate
def is_email_address_owner(user, email_address):
    return user.id == email_address.user_id


@predicate
def email_address_is_confirmed(user, email_address):
    return email_address.is_confirmed


@predicate
def email_address_is_primary(user, email_address):
    return email_address.is_primary


@predicate
def email_address_is_only_confirmed_email(user, email_address):
    return (email_address.is_confirmed) and (email_address.user.email_addresses.filter(is_confirmed=True).count() == 1)


@predicate
def has_access_perm_for_email_address(user, email_address):
    return _has_access_perm_for_obj(user=user, other_user=email_address.user, access=email_address.access)


if (not (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID)):
    add_perm('accounts.view_profile', has_access_perm & ~there_is_block)
    add_perm('accounts.view_profile_header', has_access_perm)
    add_perm('accounts.view_profile_info', has_access_perm)
    add_perm('accounts.view_profile_age', has_access_perm & has_access_perm_for_dob_day_month & has_access_perm_for_dob_year)
    add_perm('accounts.view_user_on_speedy_net_widget', always_deny)
    add_perm('accounts.view_user_on_speedy_match_widget', has_access_perm & ~is_self & ~there_is_block & view_user_on_speedy_match_widget)  # Widget doesn't display anything if there is no match; Users will not see a link to their own Speedy Match profile on Speedy Net.

add_perm('accounts.view_profile_username', has_access_perm & is_self)
add_perm('accounts.view_profile_dob_day_month', has_access_perm & has_access_perm_for_dob_day_month)
add_perm('accounts.view_profile_dob_year', has_access_perm & has_access_perm_for_dob_year)
add_perm('accounts.edit_profile', has_access_perm & is_self)
add_perm('accounts.confirm_useremailaddress', is_email_address_owner & ~email_address_is_confirmed)
add_perm('accounts.delete_useremailaddress', is_email_address_owner & ~email_address_is_primary & ~email_address_is_only_confirmed_email)
add_perm('accounts.setprimary_useremailaddress', is_email_address_owner & email_address_is_confirmed)
add_perm('accounts.change_useremailaddress', is_email_address_owner)
add_perm('accounts.view_useremailaddress', email_address_is_confirmed & has_access_perm_for_email_address)


