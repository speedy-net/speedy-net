import os

from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.core.models import TimeStampedModel, RegularUDIDField, generate_regular_udid


def uuid_dir(instance, filename):
    str_id = str(instance.id)
    return '/'.join([
        str_id[:1],
        str_id[:2],
        str_id[:4],
        filename,
    ])


class File(TimeStampedModel):
    id = RegularUDIDField()
    owner = models.ForeignKey(verbose_name=_('owner'), to='accounts.Entity', on_delete=models.SET_NULL, null=True)
    file = models.FileField(verbose_name=_('file'), upload_to=uuid_dir)
    is_stored = models.BooleanField(verbose_name=_('is stored'), default=False)
    size = models.PositiveIntegerField(verbose_name=_('file_size'), default=0)

    class Meta:
        verbose_name = _('file')
        verbose_name_plural = _('uploaded files')

    def __init__(self, *args, **kwargs):
        if not kwargs.get('id'):
            kwargs['id'] = generate_regular_udid()
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.basename

    def save(self, **kwargs):
        self.size = self.file.size
        return super().save(**kwargs)

    def store(self):
        self.is_stored = True
        self.save(update_fields={'is_stored', 'size'})

    @property
    def basename(self):
        return os.path.basename(self.file.name)


class Image(File):
    class Meta:
        verbose_name = _('images')
        verbose_name_plural = _('uploaded images')
