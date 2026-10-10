"""
Models of the Speedy Composer accounts app: the base node model of Speedy Composer and the Speedy Composer site profile.
"""
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from speedy.core.base.models import TimeStampedModel
from speedy.core.accounts.models import SiteProfileBase, User


# ~~~~ TODO: Create a node in speedy.core which will be used in all Speedy Net websites. This node should contain a username (which is the slug without dashes), slug and name. Also check that the full path after the domain name is unique in each website. But it doesn't have to be unique across different websites (such as Speedy Net and Speedy Composer).
# ~~~~ TODO: This node should be a base for each website's node. For example in Speedy Net nodes can be albums and photos. Each node will have a unique URL, albums will start with the user/page or an entity's slug and then the album's slug (which is unique only per entity) and a photo's URL will be the album's URL + the photo's slug (which will be unique per album). A photo must be linked to exactly one album.
# ~~~~ TODO: https://trello.com/c/gaKvb9eG/4-fix-model-hierarchy-and-speedy-composer-tests
class SpeedyComposerNode(TimeStampedModel):  # ~~~~ TODO: check which class we want to inherit from?
    """
    Abstract base class for a Speedy Composer node (e.g. a username, slug and name container).
    """
    # ~~~~ TODO: move to django_settings.
    # MIN_USERNAME_LENGTH = 1
    # MAX_USERNAME_LENGTH = 200
    # MIN_SLUG_LENGTH = 1
    # MAX_SLUG_LENGTH = 200
    # MIN_NAME_LENGTH = 1
    # MAX_NAME_LENGTH = 200

    class Meta:
        abstract = True

    def __str__(self):
        """
        Return the node's name as its string representation.

        :return: The name of the node.
        :rtype: str
        """
        return '{}'.format(self.name)  # ~~~~ TODO: fix!


class SiteProfile(SiteProfileBase):
    """
    Speedy Composer site-specific user profile.

    Attributes:
        RELATED_NAME (str): The related name used on the User model to access this profile.
        DELETED_NAME (str): The name to display for a deleted user's profile.
        user (User): The user associated with the profile.
        is_active (bool): Whether the Speedy Composer profile is active.

    Methods:
        is_active_and_valid(self): Check if the profile is active and valid.
        __str__(self): Get a string representation of the profile.
        _get_deleted_name(self): Get the name to display for a deleted user's profile.
        activate(self): Activate the profile.
        deactivate(self): Deactivate the profile.
        get_name(self): Get the name of the profile.
    """
    # Name of the reverse one-to-one accessor from User to this site profile (User.speedy_composer_site_profile).
    RELATED_NAME = 'speedy_composer_site_profile'

    # Name displayed instead of the user's name after the user is deleted.
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
        verbose_name = _('Speedy Composer Profile')
        verbose_name_plural = _('Speedy Composer Profiles')
        ordering = ('-last_visit', 'user_id')

    def __str__(self):
        """
        Return a string representation of the profile.

        :return: The user's string representation followed by the site name.
        :rtype: str
        """
        return '{} @ Speedy Composer'.format(super().__str__())

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


