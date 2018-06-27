from friendship.models import Friend
from rules import predicate, add_perm

from speedy.core.blocks.rules import is_self, there_is_block
from .models import UserAccessField


def _has_access_perm_for_obj(user, other, access):
    if access == UserAccessField.ACCESS_ANYONE:
        return True
    if user.is_authenticated:
        if access == UserAccessField.ACCESS_ME:
            return user == other
        if access == UserAccessField.ACCESS_FRIENDS:
            return (user == other) or Friend.objects.are_friends(user1=user, user2=other)
        if access == UserAccessField.ACCESS_FRIENDS_AND_FRIENDS_OF_FRIENDS:
            return (user == other) or Friend.objects.are_friends(user1=user, user2=other)
    return False


@predicate
def has_access_perm(user, other):
    return True


@predicate
def has_access_perm_for_dob_day_month(user, other):
    return _has_access_perm_for_obj(user=user, other=other, access=other.access_dob_day_month)


@predicate
def has_access_perm_for_dob_year(user, other):
    return _has_access_perm_for_obj(user=user, other=other, access=other.access_dob_year)


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
    return _has_access_perm_for_obj(user=user, other=email_address.user, access=email_address.access)


add_perm('accounts.view_profile', has_access_perm & ~there_is_block)
add_perm('accounts.view_profile_username', is_self)
add_perm('accounts.view_profile_header', has_access_perm)
add_perm('accounts.view_profile_info', has_access_perm)
add_perm('accounts.view_profile_dob_day_month', has_access_perm_for_dob_day_month)
add_perm('accounts.view_profile_dob_year', has_access_perm_for_dob_year)
add_perm('accounts.view_profile_age', has_access_perm_for_dob_day_month & has_access_perm_for_dob_year)
add_perm('accounts.edit_profile', is_self)
add_perm('accounts.confirm_useremailaddress', is_email_address_owner & ~email_address_is_confirmed)
add_perm('accounts.delete_useremailaddress', is_email_address_owner & ~email_address_is_primary)
add_perm('accounts.setprimary_useremailaddress', is_email_address_owner & email_address_is_confirmed)
add_perm('accounts.change_useremailaddress', is_email_address_owner)
add_perm('accounts.view_useremailaddress', email_address_is_confirmed & has_access_perm_for_email_address)
