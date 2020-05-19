from django.db import models
from django.utils.translation import gettext_lazy as _


class UserAccessField(models.SmallIntegerField):
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
        kwargs.update({
            'choices': self.ACCESS_CHOICES,
        })
        super().__init__(*args, **kwargs)


