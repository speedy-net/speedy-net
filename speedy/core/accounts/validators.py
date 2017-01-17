from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from speedy.core.base.utils import normalize_username


def reserved_username_validator(value):
    if normalize_username(slug=value) in [normalize_username(slug=reserved) for reserved in settings.UNAVAILABLE_USERNAMES]:
        raise ValidationError(_('This username is already taken.'))


def generate_regex_validator(allow_dashes=False, allow_letters_after_digits=False):
    letters = r'a-z'
    digits = r'0-9'
    symbols = r'\-' if allow_dashes else r''
    regex = r'[' + letters + symbols + ']{4,}[' + digits + symbols + ']*'
    if allow_letters_after_digits:
        regex += r'[' + letters + digits + symbols + ']*'
    if allow_letters_after_digits:
        invalid_regex_message = _("Username must start with 4 or more letters, and may contain letters, digits or dashes.")
    else:
        invalid_regex_message = _("Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.")
    return validators.RegexValidator(regex=r'^(' + regex + ')$', message=invalid_regex_message)


def get_slug_validators(min_length, max_length, allow_letters_after_digits):
    return [
        generate_regex_validator(allow_dashes=True, allow_letters_after_digits=allow_letters_after_digits),
        reserved_username_validator,
        validators.MinLengthValidator(min_length),
        validators.MaxLengthValidator(max_length),
    ]


def get_username_validators(min_length, max_length, allow_letters_after_digits):
    return [
        generate_regex_validator(allow_dashes=False, allow_letters_after_digits=allow_letters_after_digits),
        reserved_username_validator,
        validators.MinLengthValidator(min_length),
        validators.MaxLengthValidator(max_length),
    ]
