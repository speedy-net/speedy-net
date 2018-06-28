from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.core.accounts.models import Entity
from speedy.core.base.models import TimeStampedModel
from .managers import BlockManager


class Block(TimeStampedModel):
    blocker = models.ForeignKey(to=Entity, verbose_name=_('user'), on_delete=models.SET_NULL, null=True, related_name='+')
    blockee = models.ForeignKey(to=Entity, verbose_name=_('blocked user'), on_delete=models.SET_NULL, null=True, related_name='+')

    objects = BlockManager()

    class Meta:
        verbose_name = _('block')
        verbose_name_plural = _('user blocks')
        unique_together = ('blocker', 'blockee')

