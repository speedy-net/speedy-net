from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

invalid_regex_message = _(
    'Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.')


def reserved_username_validator(value):
    from .models import normalize_username
    if normalize_username(value) in [normalize_username(reserved) for reserved in settings.UNAVAILABLE_USERNAMES]:
        raise ValidationError(_('This username is already taken.'))


def get_slug_validators(min_length, max_length):
    return [
        validators.RegexValidator(regex=r'^([a-z]{4,}[0-9]{0,})$', message=invalid_regex_message),
        reserved_username_validator,
        validators.MinLengthValidator(min_length),
        validators.MaxLengthValidator(max_length),
    ]


def get_username_validators(min_length, max_length):
    return [
        validators.RegexValidator(regex=r'^([a-z\-\._]{4,}[0-9\-\._]{0,})$', message=invalid_regex_message),
        reserved_username_validator,
        validators.MinLengthValidator(min_length),
        validators.MaxLengthValidator(max_length),
    ]
