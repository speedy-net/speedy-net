import random
import string

from django.core import validators
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _

REGULAR_UDID_LENGTH = 20
SMALL_UDID_LENGTH = 15

regular_udid_validator = validators.RegexValidator(regex=r'^[1-9][0-9]{19}$', message="id contains illegal characters")
small_udid_validator = validators.RegexValidator(regex=r'^[1-9][0-9]{14}$', message="id contains illegal characters")


def _generate_udid(length):
    digits = string.digits
    digits_without_zero = digits[1:]
    return ''.join(random.choice(digits if i > 0 else digits_without_zero) for i in range(length))


def generate_regular_udid():
    return _generate_udid(length=REGULAR_UDID_LENGTH)


def generate_small_udid():
    return _generate_udid(length=SMALL_UDID_LENGTH)


# Export generate_regular_udid as generate_confirmation_token.
generate_confirmation_token = generate_regular_udid


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


