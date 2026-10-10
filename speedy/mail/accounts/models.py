from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from speedy.core.accounts.models import SiteProfileBase, User


class SiteProfile(SiteProfileBase):
    """
    Speedy Mail Software site-specific user profile.

    Attributes:
        RELATED_NAME (str): The related name used on the User model to access this profile.
        DELETED_NAME (str): The name to display for a deleted user's profile.
        user (User): The user associated with the profile.
        is_active (bool): Whether the Speedy Mail Software profile is active.

    Methods:
        is_active_and_valid(self): Check if the profile is active and valid.
        __str__(self): Get a string representation of the profile.
        _get_deleted_name(self): Get the name to display for a deleted user's profile.
        activate(self): Activate the profile.
        deactivate(self): Deactivate the profile.
        get_name(self): Get the name of the profile.
    """
    RELATED_NAME = 'speedy_mail_site_profile'

    DELETED_NAME = _('Speedy Net User')

    user = models.OneToOneField(to=User, verbose_name=_('User'), primary_key=True, on_delete=models.CASCADE, related_name=RELATED_NAME)
    is_active = models.BooleanField(default=False)

    @cached_property
    def is_active_and_valid(self):
        """
        Check if the profile is active and valid.

        :return: True if the profile is active, False otherwise.
        :rtype: bool
        """
        return (self.is_active)

    class Meta:
        verbose_name = _('Speedy Mail Profile')
        verbose_name_plural = _('Speedy Mail Profiles')
        ordering = ('-last_visit', 'user_id')

    def __str__(self):
        """
        Return a string representation of the profile.

        :return: The user's string representation followed by the site name.
        :rtype: str
        """
        return '{} @ Speedy Mail Software'.format(super().__str__())

    def _get_deleted_name(self):
        """
        Get the name to display for a deleted user's profile.

        :return: The deleted user's display name.
        :rtype: str
        """
        return self.__class__.DELETED_NAME

    def activate(self):
        """
        Activate the profile and save the user and profile.
        """
        self.is_active = True
        self.user.save_user_and_profile()

    def deactivate(self):
        """
        Deactivate the profile and save the user and profile.
        """
        self.is_active = False
        self.user.save_user_and_profile()

    def get_name(self):
        """
        Get the name of the profile.

        :return: The deleted user's display name if the user is deleted, otherwise the user's full name.
        :rtype: str
        """
        if (self.user.is_deleted):
            return self._get_deleted_name()
        return self.user.get_full_name()


