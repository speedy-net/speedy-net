from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.core.models import TimeStampedModel
from speedy.net.accounts.models import Entity
from .managers import BlockManager


class Block(TimeStampedModel):
    class Meta:
        verbose_name = _('block')
        verbose_name_plural = _('user blocks')
        unique_together = ('blocker', 'blockee')

    blocker = models.ForeignKey(verbose_name=_('user'), to=Entity, on_delete=models.SET_NULL, null=True,
                                related_name='+')
    blockee = models.ForeignKey(verbose_name=_('blocked user'), to=Entity, on_delete=models.SET_NULL, null=True,
                                related_name='+')

    objects = BlockManager()
