from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .utils import REGULAR_UDID_LENGTH, SMALL_UDID_LENGTH, generate_regular_udid, generate_small_udid
from .validators import regular_udid_validator, small_udid_validator


class ValidateModelMixin(object):
    def save(self, *args, **kwargs):
        """Call `full_clean` before saving."""
        self.full_clean()
        return super().save(*args, **kwargs)


# class BaseModel(ValidateModelMixin, models.Model): # ~~~~ TODO: doesn't work, most of the tests fail, fix and remove the following line.
class BaseModel(models.Model):
    def save(self, *args, **kwargs):
        try:
            field = self._meta.get_field('id')
            if not self.id and hasattr(field, 'id_generator'):
                self.id = field.id_generator()
                while self._meta.model.objects.filter(id=self.id).exists():
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

    def __init__(self, **kwargs):
        defaults = {
            'verbose_name': _('ID'),
            'primary_key': True,
            'db_index': True,
            'unique': True,
        }
        defaults.update(kwargs)
        super().__init__(**defaults)


class RegularUDIDField(UDIDField):
    id_generator = staticmethod(generate_regular_udid)

    def __init__(self, **kwargs):
        defaults = {
            'max_length': REGULAR_UDID_LENGTH,
            'validators': [regular_udid_validator],
        }
        defaults.update(kwargs)
        super().__init__(**defaults)


class SmallUDIDField(UDIDField):
    id_generator = staticmethod(generate_small_udid)

    def __init__(self, **kwargs):
        defaults = {
            'max_length': SMALL_UDID_LENGTH,
            'validators': [small_udid_validator],
        }
        defaults.update(kwargs)
        super().__init__(**defaults)


