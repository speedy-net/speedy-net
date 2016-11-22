import random
import string

from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _

ID_LENGTH = 20

id_validator = validators.RegexValidator(regex=r'[0-9]', message="id contains illegal characters")


def generate_id():
    digits = string.digits
    digits_without_zero = digits[1:]
    return ''.join(random.choice(digits if i > 0 else digits_without_zero) for i in range(ID_LENGTH))


# Export generate_id as generate_confirmation_token.
generate_confirmation_token = generate_id


class TimeStampedModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class UDIDField(models.CharField):
    def __init__(self, **kwargs):
        kwargs.update({
            'verbose_name': _('ID'),
            'max_length': ID_LENGTH,
            'validators': [id_validator],
            'primary_key': True,
            'db_index': True,
            'unique': True,
            'default': generate_id,
        })
        super().__init__(**kwargs)
