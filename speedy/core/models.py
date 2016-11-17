import random
import string

from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _

UDID_LENGTH = 15
BIG_UDID_LENGTH = 20

udid_validator = validators.RegexValidator(regex=r'^[1-9][0-9]{14,19}$', message="id contains illegal characters")
big_udid_validator = udid_validator


def generate_udid(length=UDID_LENGTH):
    digits = string.digits
    digits_without_zero = digits[1:]
    return ''.join(random.choice(digits if i > 0 else digits_without_zero) for i in range(length))


def generate_big_udid():
    return generate_udid(length=BIG_UDID_LENGTH)


# Export generate_id as generate_confirmation_token.
generate_confirmation_token = generate_id


class TimeStampedModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class UDIDField(models.CharField):
    def __init__(self, **kwargs):
        defaults = {
            'verbose_name': _('ID'),
            'max_length': UDID_LENGTH,
            'validators': [udid_validator],
            'primary_key': True,
            'db_index': True,
            'unique': True,
            'default': generate_udid,
        }
        defaults.update(kwargs)
        super().__init__(**defaults)


class BigUDIDField(UDIDField):
    def __init__(self, **kwargs):
        defaults = {
            'max_length': BIG_UDID_LENGTH,
            'validators': [big_udid_validator],
            'default': generate_big_udid,
        }
        defaults.update(kwargs)
        super().__init__(**defaults)
