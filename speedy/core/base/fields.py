from django.conf import settings as django_settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .utils import generate_regular_udid, generate_small_udid
from . import validators as speedy_core_base_validators


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


