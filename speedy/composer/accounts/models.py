from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.core.accounts.models import SiteProfileBase
from speedy.core.base.models import TimeStampedModel


# ~~~~ TODO: Create a node in speedy.core which will be used in all Speedy Net websites. This node should contain a username (which is the slug without dashes), slug and name. Also check that the full path after the domain name is unique in each website. But it doesn't have to be unique across different websites (such as Speedy Net and Speedy Composer).
# ~~~~ TODO: This node should be a base for each website's node. For example in Speedy Net nodes can be albums and photos. Each node will have a unique URL, albums will start with the user/page or an entity's slug and then the album's slug (which is unique only per entity) and a photo's URL will be the album's URL + the photo's slug (which will be unique per album). A photo must be linked to exactly one album.
# ~~~~ TODO: https://trello.com/c/gaKvb9eG/4-fix-model-hierarchy-and-speedy-composer-tests
class SpeedyComposerNode(TimeStampedModel): # ~~~~ TODO: check which class we want to inherit from?
    MIN_USERNAME_LENGTH = 1
    MAX_USERNAME_LENGTH = 200
    MIN_SLUG_LENGTH = 1
    MAX_SLUG_LENGTH = 200
    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 200

    class Meta:
        abstract = True

    def __str__(self):
        return '{}'.format(self.name) # ~~~~ TODO: fix!


class SiteProfile(SiteProfileBase):
    class Meta:
        verbose_name = 'Speedy Composer Profile'
        verbose_name_plural = 'Speedy Composer Profiles'

    is_active = models.BooleanField(verbose_name=_('indicates if a user has ever logged in to the site'), default=False)

    def activate(self):
        self.is_active = True
        self.save(update_fields={'is_active'})

    def deactivate(self):
        self.is_active = False
        self.save(update_fields={'is_active'})

    def get_name(self):
        return self.user.get_full_name()

