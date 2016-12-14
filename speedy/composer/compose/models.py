from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.composer.accounts.models import SpeedyComposerNamedEntity


class ChordsTemplate(SpeedyComposerNamedEntity):

    class Meta:
        verbose_name = _('chords template')
        verbose_name_plural = _('chords templates')


class Accompaniment(SpeedyComposerNamedEntity):

    class Meta:
        verbose_name = _('accompaniment')
        verbose_name_plural = _('accompaniments')


class Folder(SpeedyComposerNamedEntity):
    user = models.ForeignKey(verbose_name=_('user'), to=settings.AUTH_USER_MODEL, related_name='+')

    class Meta:
        verbose_name = _('folder')
        verbose_name_plural = _('folders')


class Composition(SpeedyComposerNamedEntity):
    folder = models.ForeignKey(verbose_name=_('folder'), to=Folder, related_name='+')
    chords_template = models.ForeignKey(verbose_name=_('chords template'), to=ChordsTemplate, related_name='+')
    accompaniment = models.ForeignKey(verbose_name=_('accompaniment'), to=Accompaniment, related_name='+')
    tempo = models.SmallIntegerField(verbose_name=_('tempo'), default=105)
    public = models.BooleanField(verbose_name=_('public'), default=False)

    class Meta:
        verbose_name = _('composition')
        verbose_name_plural = _('compositions')


