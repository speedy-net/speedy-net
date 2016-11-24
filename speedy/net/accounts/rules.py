from django.utils import translation
from friendship.models import Friend
from rules import predicate, add_perm

from speedy.net.blocks.rules import is_blocked, is_self
from .models import ACCESS_ANYONE, ACCESS_ME, ACCESS_FRIENDS, ACCESS_FRIENDS_2


def _has_access_perm_for_obj(user, other, access):
    if access == ACCESS_ANYONE:
        return True
    if user.is_authenticated():
        if access == ACCESS_ME:
            return user == other
        if access == ACCESS_FRIENDS:
            return (user == other) or Friend.objects.are_friends(user, other)
        if access == ACCESS_FRIENDS_2:
            return (user == other) or Friend.objects.are_friends(user, other)
    return False


@predicate
def has_access_perm(user, other):
    return _has_access_perm_for_obj(user, other, other.profile.access_account)


@predicate
def has_access_perm_for_dob_day_month(user, other):
    return _has_access_perm_for_obj(user, other, other.profile.access_dob_day_month)


@predicate
def has_access_perm_for_dob_year(user, other):
    return _has_access_perm_for_obj(user, other, other.profile.access_dob_year)


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
def has_access_perm_for_email_address(user, email_address):
    return _has_access_perm_for_obj(user, email_address.user, email_address.access)


add_perm('accounts.view_profile', has_access_perm & ~is_blocked)
add_perm('accounts.view_profile_username', is_self)
add_perm('accounts.view_profile_info', has_access_perm)
add_perm('accounts.view_profile_dob_day_month', has_access_perm_for_dob_day_month)
add_perm('accounts.view_profile_dob_year', has_access_perm_for_dob_year)
add_perm('accounts.edit_profile', is_self)
add_perm('accounts.confirm_useremailaddress', is_email_address_owner & ~email_address_is_confirmed)
add_perm('accounts.delete_useremailaddress', is_email_address_owner & ~email_address_is_primary)
add_perm('accounts.setprimary_useremailaddress', is_email_address_owner & email_address_is_confirmed)
add_perm('accounts.change_useremailaddress', is_email_address_owner)
add_perm('accounts.view_useremailaddress', email_address_is_confirmed & has_access_perm_for_email_address)
