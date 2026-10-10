from django.db import models
from django.utils.translation import gettext_lazy as _


class UserAccessField(models.SmallIntegerField):
    """
    A small integer field representing who may access a given piece of profile information.

    Attributes:
        ACCESS_ME (int): Only the user themselves can access.
        ACCESS_FRIENDS (int): The user and their friends can access.
        ACCESS_FRIENDS_AND_FRIENDS_OF_FRIENDS (int): The user, their friends and friends of friends can access.
        ACCESS_ANYONE (int): Anyone can access.
        ACCESS_CHOICES (tuple): The available choices for this field.
    """
    ACCESS_ME = 1
    ACCESS_FRIENDS = 2
    ACCESS_FRIENDS_AND_FRIENDS_OF_FRIENDS = 3
    ACCESS_ANYONE = 4

    ACCESS_CHOICES = (
        (ACCESS_ME, _('Only me')),
        (ACCESS_FRIENDS, _('Me and my friends')),
        # (ACCESS_FRIENDS_AND_FRIENDS_OF_FRIENDS, _('Me, my friends and friends of my friends')),
        (ACCESS_ANYONE, _('Anyone')),
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the field, forcing its choices to the predefined access choices.

        :param args: Positional arguments passed to the parent field.
        :param kwargs: Keyword arguments passed to the parent field.
        """
        kwargs.update({
            'choices': self.ACCESS_CHOICES,
        })
        super().__init__(*args, **kwargs)


