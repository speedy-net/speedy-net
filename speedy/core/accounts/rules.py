"""
Permission rules of the Speedy Core accounts app, controlling access to user profiles, user details and email addresses.
"""
from django.conf import settings as django_settings

from rules import predicate, add_perm, always_deny

from speedy.core.accounts.base_rules import is_self, is_active
from speedy.core.friends.rules import are_friends
from speedy.core.blocks.rules import there_is_block
from .fields import UserAccessField
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


def _has_access_perm_for_obj(user, other_user, access):
    """
    Check whether the given user has access to another user's field, based on the field's access setting.

    :param user: The user requesting access.
    :type user: speedy.core.accounts.models.User
    :param other_user: The user whose field is being accessed.
    :type other_user: speedy.core.accounts.models.User
    :param access: The access setting of the field (one of ``UserAccessField``'s choices).
    :type access: str
    :return: True if the access is granted, False otherwise.
    :rtype: bool
    """
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
    """
    Check whether the user is granted general access to another user's profile - staff superusers always have access, otherwise access requires the other user's profile to be active.

    :param user: The user requesting access.
    :type user: speedy.core.accounts.models.User
    :param other_user: The user whose profile is being accessed.
    :type other_user: speedy.core.accounts.models.User
    :return: True if access is granted, False otherwise.
    :rtype: bool
    """
    if (user.is_authenticated):
        if ((user.is_staff) and (user.is_superuser)):
            return True
    return is_active(user=user, other_user=other_user)


@predicate
def has_access_perm_for_dob_day_month(user, other_user):
    """
    Check whether the user has access to the other user's date of birth day and month, based on the other user's access setting for that field.

    :param user: The user requesting access.
    :type user: speedy.core.accounts.models.User
    :param other_user: The user whose date of birth day and month is being accessed.
    :type other_user: speedy.core.accounts.models.User
    :return: True if access is granted, False otherwise.
    :rtype: bool
    """
    return _has_access_perm_for_obj(user=user, other_user=other_user, access=other_user.access_dob_day_month)


@predicate
def has_access_perm_for_dob_year(user, other_user):
    """
    Check whether the user has access to the other user's date of birth year, based on the other user's access setting for that field.

    :param user: The user requesting access.
    :type user: speedy.core.accounts.models.User
    :param other_user: The user whose date of birth year is being accessed.
    :type other_user: speedy.core.accounts.models.User
    :return: True if access is granted, False otherwise.
    :rtype: bool
    """
    return _has_access_perm_for_obj(user=user, other_user=other_user, access=other_user.access_dob_year)


@predicate
def view_user_on_speedy_match_widget(user, other_user):
    """
    Check whether the user may see the other user displayed in the "view on Speedy Match" widget - staff superusers always may, otherwise the user must have a matching rank with the other user above rank 0.

    :param user: The user requesting access.
    :type user: speedy.core.accounts.models.User
    :param other_user: The user being considered for display in the widget.
    :type other_user: speedy.core.accounts.models.User
    :return: True if the widget may be displayed, False otherwise.
    :rtype: bool
    """
    if (user.is_authenticated):
        if ((user.is_staff) and (user.is_superuser)):
            return True
        match_profile = (user.speedy_match_profile.get_matching_rank(other_profile=other_user.speedy_match_profile) > SpeedyMatchSiteProfile.RANK_0)
        return match_profile
    return False


@predicate
def is_email_address_owner(user, email_address):
    """
    Check whether the given user owns the given email address.

    :param user: The user requesting access.
    :type user: speedy.core.accounts.models.User
    :param email_address: The email address being checked.
    :type email_address: speedy.core.accounts.models.UserEmailAddress
    :return: True if the user owns the email address, False otherwise.
    :rtype: bool
    """
    return user.id == email_address.user_id


@predicate
def email_address_is_confirmed(user, email_address):
    """
    Check whether the given email address is confirmed.

    :param user: The user requesting access (unused, required for the predicate signature).
    :type user: speedy.core.accounts.models.User
    :param email_address: The email address being checked.
    :type email_address: speedy.core.accounts.models.UserEmailAddress
    :return: True if the email address is confirmed, False otherwise.
    :rtype: bool
    """
    return email_address.is_confirmed


@predicate
def email_address_is_primary(user, email_address):
    """
    Check whether the given email address is the user's primary email address.

    :param user: The user requesting access (unused, required for the predicate signature).
    :type user: speedy.core.accounts.models.User
    :param email_address: The email address being checked.
    :type email_address: speedy.core.accounts.models.UserEmailAddress
    :return: True if the email address is primary, False otherwise.
    :rtype: bool
    """
    return email_address.is_primary


@predicate
def email_address_is_only_confirmed_email(user, email_address):
    """
    Check whether the given email address is confirmed and is the only confirmed email address belonging to its owner.

    :param user: The user requesting access (unused, required for the predicate signature).
    :type user: speedy.core.accounts.models.User
    :param email_address: The email address being checked.
    :type email_address: speedy.core.accounts.models.UserEmailAddress
    :return: True if the email address is confirmed and is the only confirmed email address of its owner, False otherwise.
    :rtype: bool
    """
    return (email_address.is_confirmed) and (email_address.user.email_addresses.filter(is_confirmed=True).count() == 1)


@predicate
def has_access_perm_for_email_address(user, email_address):
    """
    Check whether the user has access to the given email address, based on the email address's owner's access setting for that field.

    :param user: The user requesting access.
    :type user: speedy.core.accounts.models.User
    :param email_address: The email address being accessed.
    :type email_address: speedy.core.accounts.models.UserEmailAddress
    :return: True if access is granted, False otherwise.
    :rtype: bool
    """
    return _has_access_perm_for_obj(user=user, other_user=email_address.user, access=email_address.access)


if (not (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID)):
    add_perm(name='accounts.view_profile', pred=has_access_perm & ~there_is_block)
    add_perm(name='accounts.view_profile_header', pred=has_access_perm)
    add_perm(name='accounts.view_profile_info', pred=has_access_perm)
    add_perm(name='accounts.view_profile_age', pred=has_access_perm & has_access_perm_for_dob_day_month & has_access_perm_for_dob_year)
    add_perm(name='accounts.view_user_on_speedy_net_widget', pred=always_deny)
    add_perm(name='accounts.view_user_on_speedy_match_widget', pred=has_access_perm & ~is_self & ~there_is_block & view_user_on_speedy_match_widget)  # Widget doesn't display anything if there is no match; Users will not see a link to their own Speedy Match profile on Speedy Net.

add_perm(name='accounts.view_profile_username', pred=has_access_perm & is_self)
add_perm(name='accounts.view_profile_dob_day_month', pred=has_access_perm & has_access_perm_for_dob_day_month)
add_perm(name='accounts.view_profile_dob_year', pred=has_access_perm & has_access_perm_for_dob_year)
add_perm(name='accounts.edit_profile', pred=is_self)
add_perm(name='accounts.confirm_useremailaddress', pred=is_email_address_owner & ~email_address_is_confirmed)
add_perm(name='accounts.delete_useremailaddress', pred=is_email_address_owner & ~email_address_is_primary & ~email_address_is_only_confirmed_email)
add_perm(name='accounts.setprimary_useremailaddress', pred=is_email_address_owner & email_address_is_confirmed)
add_perm(name='accounts.change_useremailaddress', pred=is_email_address_owner)
add_perm(name='accounts.view_useremailaddress', pred=email_address_is_confirmed & has_access_perm_for_email_address)


