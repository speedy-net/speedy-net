from django.conf import settings as django_settings
from django.core.exceptions import FieldDoesNotExist
from django.contrib.auth.models import BaseUserManager as DjangoBaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from .utils import generate_regular_udid, generate_small_udid
from . import validators as speedy_core_base_validators


class ValidateModelMixin(object):
    def save(self, *args, **kwargs):
        """
        Call `full_clean` before saving.
        """
        self.full_clean()
        return super().save(*args, **kwargs)


class ManagerMixin(object):
    def bulk_create(self, *args, **kwargs):
        raise NotImplementedError("bulk_create is not implemented.")


class BaseManager(ManagerMixin, models.Manager):
    pass


class BaseUserManager(ManagerMixin, DjangoBaseUserManager):
    pass


class BaseModel(ValidateModelMixin, models.Model):
    objects = BaseManager()

    def save(self, *args, **kwargs):
        try:
            field = self._meta.get_field('id')
            if ((not (self.id)) and (hasattr(field, 'id_generator'))):
                self.id = field.id_generator()
                while (self._meta.model.objects.filter(id=self.id).exists()):
                    self.id = field.id_generator()
        except FieldDoesNotExist:
            pass
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True


class TimeStampedModel(BaseModel):
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


# Never use this class directly. Only use inherited classes below.
class UDIDField(models.CharField):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        given_kwargs = kwargs
        defaults = {
            'verbose_name': _('ID'),
            'primary_key': True,
            'db_index': True,
            'unique': True,
        }
        kwargs = defaults
        kwargs.update(given_kwargs)
        super().__init__(*args, **kwargs)


class SmallUDIDField(UDIDField):
    id_generator = staticmethod(generate_small_udid)

    def __init__(self, *args, **kwargs):
        given_kwargs = kwargs
        defaults = {
            'max_length': django_settings.SMALL_UDID_LENGTH,
            'validators': [speedy_core_base_validators.small_udid_validator],
        }
        kwargs = defaults
        kwargs.update(given_kwargs)
        super().__init__(*args, **kwargs)


class RegularUDIDField(UDIDField):
    id_generator = staticmethod(generate_regular_udid)

    def __init__(self, *args, **kwargs):
        given_kwargs = kwargs
        defaults = {
            'max_length': django_settings.REGULAR_UDID_LENGTH,
            'validators': [speedy_core_base_validators.regular_udid_validator],
        }
        kwargs = defaults
        kwargs.update(given_kwargs)
        super().__init__(*args, **kwargs)


