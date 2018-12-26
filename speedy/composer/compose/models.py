from django.conf import settings as django_settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from speedy.composer.accounts.models import SpeedyComposerNode


class ChordsTemplate(SpeedyComposerNode):

    class Meta:
        verbose_name = _('chords template')
        verbose_name_plural = _('chords templates')


class Accompaniment(SpeedyComposerNode):

    class Meta:
        verbose_name = _('accompaniment')
        verbose_name_plural = _('accompaniments')


class Folder(SpeedyComposerNode):
    user = models.ForeignKey(to=django_settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE, related_name='+')

    class Meta:
        verbose_name = _('folder')
        verbose_name_plural = _('folders')


class Composition(SpeedyComposerNode):
    folder = models.ForeignKey(to=Folder, verbose_name=_('folder'), on_delete=models.CASCADE, related_name='+')
    chords_template = models.ForeignKey(to=ChordsTemplate, verbose_name=_('chords template'), on_delete=models.CASCADE, related_name='+')
    accompaniment = models.ForeignKey(to=Accompaniment, verbose_name=_('accompaniment'), on_delete=models.CASCADE, related_name='+')
    tempo = models.SmallIntegerField(verbose_name=_('tempo'), default=105)
    public = models.BooleanField(verbose_name=_('public'), default=False)

    class Meta:
        verbose_name = _('composition')
        verbose_name_plural = _('compositions')


