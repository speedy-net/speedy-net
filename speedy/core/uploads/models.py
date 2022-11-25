import os

from django.db import models
from django.utils.translation import gettext_lazy as _

from speedy.core.base.models import TimeStampedModel
from speedy.core.base.fields import RegularUDIDField
from speedy.core.base.utils import generate_regular_udid
from .utils import uuid_dir


class File(TimeStampedModel):
    id = RegularUDIDField()
    owner = models.ForeignKey(to='accounts.Entity', verbose_name=_('owner'), on_delete=models.SET_NULL, blank=True, null=True)
    file = models.FileField(verbose_name=_('file'), upload_to=uuid_dir)
    is_stored = models.BooleanField(verbose_name=_('is stored'), default=False)
    size = models.PositiveIntegerField(verbose_name=_('file size'), default=0)

    @property
    def basename(self):
        return os.path.basename(self.file.name)

    class Meta:
        verbose_name = _('uploaded file')
        verbose_name_plural = _('uploaded files')
        ordering = ('-date_created',)

    def __str__(self):
        return '{} (owner={})'.format(self.basename, self.owner)

    def save(self, *args, **kwargs):
        self.size = self.file.size
        return super().save(*args, **kwargs)

    def store(self):
        self.is_stored = True
        self.save()


class Image(File):
    visible_on_website = models.BooleanField(verbose_name=_('visible on website'), default=False)
    aws_image_moderation_time = models.DateTimeField(verbose_name=_('AWS image moderation time'), blank=True, null=True)
    aws_facial_analysis_time = models.DateTimeField(verbose_name=_('AWS facial analysis time'), blank=True, null=True)
    aws_raw_image_moderation_results = models.JSONField(verbose_name=_('AWS raw image moderation results'), blank=True, null=True)
    aws_raw_facial_analysis_results = models.JSONField(verbose_name=_('AWS raw facial analysis results'), blank=True, null=True)
    number_of_faces = models.PositiveSmallIntegerField(verbose_name=_('number of faces'), blank=True, null=True)

    class Meta:
        verbose_name = _('uploaded image')
        verbose_name_plural = _('uploaded images')
        ordering = ('-date_created',)


