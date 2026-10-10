from django.conf import settings as django_settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .utils import generate_regular_udid, generate_small_udid
from . import validators as speedy_core_base_validators


# Never use this class directly. Only use inherited classes below.
class UDIDField(models.CharField):
    """
    An abstract base class for unique, indexed, primary-key ID fields with a generated default value.

    Attributes:
        generate_id (callable): A static method generating a new ID value. Must be set by subclasses.

    Never use this class directly. Only use inherited classes below.
    """
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        """
        Initializes the field with default kwargs (verbose name 'ID', primary key, indexed, unique), which can be overridden by the given kwargs.

        :param args: Additional positional arguments, passed to the parent constructor.
        :param kwargs: Additional keyword arguments, overriding the defaults, passed to the parent constructor.
        """
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
    """
    A UDID field with a small length, used for most models.

    Attributes:
        generate_id (callable): Generates a new small UDID value.
    """
    generate_id = staticmethod(generate_small_udid)

    def __init__(self, *args, **kwargs):
        """
        Initializes the field with default kwargs (max length and validator for a small UDID), which can be overridden by the given kwargs.

        :param args: Additional positional arguments, passed to the parent constructor.
        :param kwargs: Additional keyword arguments, overriding the defaults, passed to the parent constructor.
        """
        given_kwargs = kwargs
        defaults = {
            'max_length': django_settings.SMALL_UDID_LENGTH,
            'validators': [speedy_core_base_validators.small_udid_validator],
        }
        kwargs = defaults
        kwargs.update(given_kwargs)
        super().__init__(*args, **kwargs)


class RegularUDIDField(UDIDField):
    """
    A UDID field with a regular (longer) length, used for models which need more unique values, such as users.

    Attributes:
        generate_id (callable): Generates a new regular UDID value.
    """
    generate_id = staticmethod(generate_regular_udid)

    def __init__(self, *args, **kwargs):
        """
        Initializes the field with default kwargs (max length and validator for a regular UDID), which can be overridden by the given kwargs.

        :param args: Additional positional arguments, passed to the parent constructor.
        :param kwargs: Additional keyword arguments, overriding the defaults, passed to the parent constructor.
        """
        given_kwargs = kwargs
        defaults = {
            'max_length': django_settings.REGULAR_UDID_LENGTH,
            'validators': [speedy_core_base_validators.regular_udid_validator],
        }
        kwargs = defaults
        kwargs.update(given_kwargs)
        super().__init__(*args, **kwargs)


