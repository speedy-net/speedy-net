"""
Base permission rule predicates of Speedy Core, checking whether two users are the same user and whether the other user's profile is active.
"""
from rules import predicate


@predicate
def is_self(user, other_user):
    """
    Check whether the user and the other user are the same user.

    :param user: The user requesting access.
    :type user: speedy.core.accounts.models.User
    :param other_user: The user being checked against.
    :type other_user: speedy.core.accounts.models.User
    :return: True if both users are the same, False otherwise.
    :rtype: bool
    """
    return user == other_user


@predicate
def is_active(user, other_user):
    """
    Check whether the other user's profile is active.

    :param user: The user requesting access.
    :type user: speedy.core.accounts.models.User
    :param other_user: The user whose profile activity is checked.
    :type other_user: speedy.core.accounts.models.User
    :return: True if the other user's profile is active, False otherwise.
    :rtype: bool
    """
    return (other_user.profile.is_active)


