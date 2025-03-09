import os

from django.db import models
from django.utils.translation import gettext_lazy as _

from speedy.core.base.models import TimeStampedModel
from speedy.core.base.fields import RegularUDIDField
from .managers import FileManager, ImageManager
from .utils import uuid_dir


class File(TimeStampedModel):
    """
    Represents a file uploaded by a user.

    Attributes:
        id (RegularUDIDField): The unique identifier for the file.
        owner (ForeignKey): The owner of the file.
        file (FileField): The file itself.
        is_stored (BooleanField): Whether the file is stored.
        size (PositiveIntegerField): The size of the file.
    """
    id = RegularUDIDField()
    owner = models.ForeignKey(to='accounts.Entity', verbose_name=_('owner'), on_delete=models.SET_NULL, blank=True, null=True)
    file = models.FileField(verbose_name=_('file'), upload_to=uuid_dir)
    is_stored = models.BooleanField(verbose_name=_('is stored'), default=False)
    size = models.PositiveIntegerField(verbose_name=_('file size'), default=0)

    objects = FileManager()

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
        """
        Save the File instance to the database.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.size = self.file.size
        return super().save(*args, **kwargs)

    def store(self):
        """
        Mark the file as stored and save it to the database.
        """
        self.is_stored = True
        self.save()


class Image(File):
    """
    Represents an image file uploaded by a user.

    Attributes:
        visible_on_website (BooleanField): Whether the image is visible on the website.
        speedy_image_moderation_time (DateTimeField): The time of Speedy image moderation.
        aws_image_moderation_time (DateTimeField): The time of AWS image moderation.
        aws_facial_analysis_time (DateTimeField): The time of AWS facial analysis.
        aws_raw_image_moderation_results (JSONField): The raw results of AWS image moderation.
        aws_raw_facial_analysis_results (JSONField): The raw results of AWS facial analysis.
        number_of_faces (PositiveSmallIntegerField): The number of faces detected in the image.
    """
    visible_on_website = models.BooleanField(verbose_name=_('visible on website'), default=False)
    speedy_image_moderation_time = models.DateTimeField(verbose_name=_('Speedy image moderation time'), blank=True, null=True)
    aws_image_moderation_time = models.DateTimeField(verbose_name=_('AWS image moderation time'), blank=True, null=True)
    aws_facial_analysis_time = models.DateTimeField(verbose_name=_('AWS facial analysis time'), blank=True, null=True)
    aws_raw_image_moderation_results = models.JSONField(verbose_name=_('AWS raw image moderation results'), blank=True, null=True)
    aws_raw_facial_analysis_results = models.JSONField(verbose_name=_('AWS raw facial analysis results'), blank=True, null=True)
    number_of_faces = models.PositiveSmallIntegerField(verbose_name=_('number of faces'), blank=True, null=True)

    objects = ImageManager()

    class Meta:
        verbose_name = _('uploaded image')
        verbose_name_plural = _('uploaded images')
        ordering = ('-date_created',)


