from friendship.models import Friend
from rules import predicate, add_perm

from .models import ACCESS_ME, ACCESS_FRIENDS, ACCESS_FRIENDS_2, ACCESS_ANYONE


@predicate
def can_view_profile(user, other):
    access = other.profile.access_account
    if access == ACCESS_ME:
        return user == other
    if access == ACCESS_FRIENDS:
        return (user == other) or Friend.objects.are_friends(user, other)
    if access == ACCESS_FRIENDS_2:
        return (user == other) or Friend.objects.are_friends(user, other)
    return True


@predicate
def is_email_address_owner(user, email_address):
    return user.id == email_address.user_id


@predicate
def email_address_is_confirmed(user, email_address):
    return email_address.is_confirmed


@predicate
def email_address_is_primary(user, email_address):
    return email_address.is_primary


add_perm('accounts.view_profile', can_view_profile)
add_perm('accounts.confirm_useremailaddress', is_email_address_owner & ~email_address_is_confirmed)
add_perm('accounts.delete_useremailaddress', is_email_address_owner & ~email_address_is_primary)
add_perm('accounts.setprimary_useremailaddress', is_email_address_owner & email_address_is_confirmed)
