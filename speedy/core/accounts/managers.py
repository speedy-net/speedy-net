"""
Model managers of the Speedy Core accounts app for entities and users.
"""
import logging

from django.db.models import Q
from django.utils.timezone import now

from speedy.core.base.managers import BaseManager, BaseUserManager
from speedy.core.base.utils import normalize_username
from .utils import normalize_email

logger = logging.getLogger(__name__)


class EntityManager(BaseManager):
    """
    Manager for the Entity model, providing lookup helpers by username (or the equivalent slug).
    """

    def get_by_username(self, username):
        """
        Get the entity whose normalized username matches the given username.

        :param username: The username to look up.
        :type username: str
        :return: The matching entity.
        :rtype: speedy.core.accounts.models.Entity
        :raises django.core.exceptions.ObjectDoesNotExist: If no entity has the given username.
        """
        return self.get(username=normalize_username(username=username))

    def get_by_slug(self, slug):
        """
        Get the entity whose normalized username matches the given slug.

        :param slug: The slug to look up (same as username).
        :type slug: str
        :return: The matching entity.
        :rtype: speedy.core.accounts.models.Entity
        :raises django.core.exceptions.ObjectDoesNotExist: If no entity has the given slug.
        """
        return self.get_by_username(username=slug)

    def filter_by_username(self, username):
        """
        Filter entities whose normalized username matches the given username.

        :param username: The username to filter by.
        :type username: str
        :return: A queryset of matching entities.
        :rtype: django.db.models.QuerySet
        """
        return self.filter(username=normalize_username(username=username))

    def filter_by_slug(self, slug):
        """
        Filter entities whose normalized username matches the given slug.

        :param slug: The slug to filter by (same as username).
        :type slug: str
        :return: A queryset of matching entities.
        :rtype: django.db.models.QuerySet
        """
        return self.filter_by_username(username=slug)


class UserManager(BaseUserManager):
    """
    Manager for the User model, handling user creation, lookup by username or email, and account deletion.

    Methods:
        normalize_email(cls, email): Normalize the email address by lowercasing it.
        _create_user(self, slug, password, **extra_fields): Create and save a user with the given username and password.
        get_queryset(self): Return the base queryset with related site profiles and photo prefetched.
        get_by_natural_key(self, username): Look up a user by username or email address.
        active(self, *args, **kwargs): Filter the queryset to only active, non-deleted users.
        create_user(self, slug, password, **extra_fields): Create and save a regular (non-staff, non-superuser) user.
        create_superuser(self, slug, password, **extra_fields): Create and save a staff superuser.
        mark_a_user_as_deleted(self, user, delete_password): Permanently mark a user as deleted.
    """

    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the email address by lowercasing it.

        :param email: The email address.
        :type email: str
        :return: The normalized email address.
        :rtype: str
        """
        email = super().normalize_email(email=email)
        email = email.lower()
        return email

    def _create_user(self, slug, password, **extra_fields):
        """
        Creates and saves a User with the given slug and password.

        :param slug: The slug (username) of the new user.
        :type slug: str
        :param password: The raw password of the new user.
        :type password: str
        :param extra_fields: Additional fields to set on the new user; gender defaults to GENDER_OTHER.
        :return: The created user.
        :rtype: speedy.core.accounts.models.User
        :raises ValueError: If the slug is empty.
        """
        extra_fields.setdefault('gender', self.model.GENDER_OTHER)
        if (not (slug)):
            raise ValueError('The given username must be set.')
        user = self.model(slug=slug, **extra_fields)
        user.set_password(raw_password=password)
        user.save(using=self._db)
        return user

    def get_queryset(self):
        """
        Return the base queryset, with the related site profiles and photo prefetched for efficiency.

        :return: A distinct queryset of users with related data prefetched.
        :rtype: django.db.models.QuerySet
        """
        from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
        return super().get_queryset().prefetch_related(SpeedyNetSiteProfile.RELATED_NAME, SpeedyMatchSiteProfile.RELATED_NAME, 'photo').distinct()

    def get_by_natural_key(self, username):
        """
        Get the user matching the given username or email address.

        :param username: The username or email address to look up.
        :type username: str
        :return: The matching user.
        :rtype: speedy.core.accounts.models.User
        :raises django.core.exceptions.ObjectDoesNotExist: If no user matches.
        :raises django.core.exceptions.MultipleObjectsReturned: If more than one user matches by username and email combined and the email alone also matches more than one user.
        """
        # If we try both the username and the email address, we can't use get() because we can have two users returned in the query.
        if (len(self.distinct().filter(Q(username=normalize_username(username=username)) | Q(email_addresses__email=normalize_email(email=username)))) > 1):
            # If there are more than one user returned in the query, use only the email address (because the username input contains "@").
            return self.distinct().get(Q(email_addresses__email=normalize_email(email=username)))
        else:
            # If no more than one user is returned in the query, use both the username and the email address.
            return self.distinct().get(Q(username=normalize_username(username=username)) | Q(email_addresses__email=normalize_email(email=username)))

    def active(self, *args, **kwargs):
        """
        Filter the queryset to only active, non-deleted users, with any additional filters applied.

        :param args: Additional positional filter arguments passed to ``filter()``.
        :param kwargs: Additional keyword filter arguments passed to ``filter()``.
        :return: A queryset of active, non-deleted users matching the additional filters.
        :rtype: django.db.models.QuerySet
        """
        return self.filter(is_active=True, is_deleted=False, *args, **kwargs)

    def create_user(self, slug, password=None, **extra_fields):
        """
        Create and save a regular user (not staff, not superuser) with the given username and password.

        :param slug: The username (slug) for the new user.
        :type slug: str
        :param password: The password for the new user.
        :type password: str
        :param extra_fields: Additional fields to set on the new user.
        :return: The newly created user.
        :rtype: speedy.core.accounts.models.User
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(slug=slug, password=password, **extra_fields)

    def create_superuser(self, slug, password, **extra_fields):
        """
        Create and save a staff superuser with the given username and password.

        :param slug: The username (slug) for the new superuser.
        :type slug: str
        :param password: The password for the new superuser.
        :type password: str
        :param extra_fields: Additional fields to set on the new superuser.
        :return: The newly created superuser.
        :rtype: speedy.core.accounts.models.User
        :raises ValueError: If ``is_staff`` or ``is_superuser`` is explicitly set to a falsy value in ``extra_fields``.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if (extra_fields.get('is_staff') is not True):
            raise ValueError('Superuser must have is_staff=True.')
        if (extra_fields.get('is_superuser') is not True):
            raise ValueError('Superuser must have is_superuser=True.')

        user = self._create_user(slug=slug, password=password, **extra_fields)
        return user

    def mark_a_user_as_deleted(self, user, delete_password):
        """
        Permanently mark a user as deleted. This is irreversible. The user will not be able to log in, and will not be able to undelete their account or activate it on Speedy Net. The name of the deleted users will not be displayed on the website and their images and email addresses will be removed.

        :param user: Required. The user to mark as deleted.
        :type user: speedy.core.accounts.models.User
        :param delete_password: Required. The password to use to mark the user as deleted.
        :type delete_password: str
        :return: None
        """
        if (not (delete_password == "Mark this user as deleted in Speedy Net.")):
            raise ValueError("The delete password is incorrect.")
        if (user.is_active):
            raise ValueError("User must be inactive to be marked as deleted.")
        if ((user.is_staff) or (user.is_superuser)):
            raise ValueError("Staff and superusers cannot be marked as deleted.")
        assert (delete_password == "Mark this user as deleted in Speedy Net.")
        assert (user.is_active is False)
        assert (user.is_staff is False)
        assert (user.is_superuser is False)

        user.set_unusable_password()
        user.save()
        user.speedy_net_profile.deactivate()
        user.speedy_match_profile.deactivate()
        user._mark_as_deleted()
        user.photo = None
        user.save()
        user.save_user_and_profile()
        for e1 in user.email_addresses.all():
            e1.delete()
        # All the other stuff will be done by command delete_unconfirmed_accounts, 60 days after the user has been deleted and 60 days after the user hasn't visited both sites.

        logger.warning("UserManager::mark_a_user_as_deleted::{user} marked as deleted. (registered {registered_days_ago} days ago).".format(
            user=user,
            registered_days_ago=(now() - user.date_created).days,
        ))


