"""
Models of the Speedy Composer compose app: chords templates, accompaniments, folders and compositions.
"""
from django.conf import settings as django_settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from speedy.composer.accounts.models import SpeedyComposerNode
from speedy.core.accounts.models import User


class ChordsTemplate(SpeedyComposerNode):
    """
    A chords template that can be used in a composition.
    """

    class Meta:
        verbose_name = _('chords template')
        verbose_name_plural = _('chords templates')


class Accompaniment(SpeedyComposerNode):
    """
    An accompaniment that can be used in a composition.
    """

    class Meta:
        verbose_name = _('accompaniment')
        verbose_name_plural = _('accompaniments')


class Folder(SpeedyComposerNode):
    """
    A folder which belongs to a user and can contain compositions.

    Attributes:
        user (User): The user who owns the folder.
    """
    user: User = models.ForeignKey(to=django_settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE, related_name='+')

    class Meta:
        verbose_name = _('folder')
        verbose_name_plural = _('folders')


class Composition(SpeedyComposerNode):
    """
    A musical composition, which belongs to a folder and uses a chords template and an accompaniment.

    Attributes:
        folder (Folder): The folder which contains the composition.
        chords_template (ChordsTemplate): The chords template used in the composition.
        accompaniment (Accompaniment): The accompaniment used in the composition.
        tempo (int): The tempo of the composition.
        public (bool): Whether the composition is public.
    """
    folder = models.ForeignKey(to=Folder, verbose_name=_('folder'), on_delete=models.CASCADE, related_name='+')
    chords_template = models.ForeignKey(to=ChordsTemplate, verbose_name=_('chords template'), on_delete=models.CASCADE, related_name='+')
    accompaniment = models.ForeignKey(to=Accompaniment, verbose_name=_('accompaniment'), on_delete=models.CASCADE, related_name='+')
    tempo = models.SmallIntegerField(verbose_name=_('tempo'), default=105)
    public = models.BooleanField(verbose_name=_('public'), default=False)

    class Meta:
        verbose_name = _('composition')
        verbose_name_plural = _('compositions')


