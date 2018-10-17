from django.conf import settings
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _, ungettext_lazy

from speedy.core.base.utils import normalize_slug, normalize_username


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
    return RegexValidator(regex=r'^(' + regex + ')$', message=invalid_regex_message)


class UsernameMinLengthValidator(MinLengthValidator):
    message = ungettext_lazy(
        singular='Username must contain at least %(limit_value)d alphanumeric character (it has %(show_value)d).',
        plural='Username must contain at least %(limit_value)d alphanumeric characters (it has %(show_value)d).',
        number='limit_value',
    )

    def clean(self, x):
        return len(normalize_username(slug=x))


class UsernameMaxLengthValidator(MaxLengthValidator):
    message = ungettext_lazy(
        singular='Username must contain at most %(limit_value)d alphanumeric character (it has %(show_value)d).',
        plural='Username must contain at most %(limit_value)d alphanumeric characters (it has %(show_value)d).',
        number='limit_value',
    )

    def clean(self, x):
        return len(normalize_username(slug=x))


class SlugMinLengthValidator(MinLengthValidator):
    message = ungettext_lazy(
        singular='Username must contain at least %(limit_value)d character (it has %(show_value)d).',
        plural='Username must contain at least %(limit_value)d characters (it has %(show_value)d).',
        number='limit_value',
    )

    def clean(self, x):
        return len(normalize_slug(slug=x))


class SlugMaxLengthValidator(MaxLengthValidator):
    message = ungettext_lazy(
        singular='Username must contain at most %(limit_value)d character (it has %(show_value)d).',
        plural='Username must contain at most %(limit_value)d characters (it has %(show_value)d).',
        number='limit_value',
    )

    def clean(self, x):
        return len(normalize_slug(slug=x))


def get_username_validators(min_username_length, max_username_length, allow_letters_after_digits):
    return [
        generate_regex_validator(allow_dashes=False, allow_letters_after_digits=allow_letters_after_digits),
        reserved_username_validator,
        UsernameMinLengthValidator(limit_value=min_username_length),
        UsernameMaxLengthValidator(limit_value=max_username_length),
        SlugMinLengthValidator(limit_value=min_username_length),
        SlugMaxLengthValidator(limit_value=max_username_length),
        MinLengthValidator(limit_value=min_username_length),
        MaxLengthValidator(limit_value=max_username_length),
    ]


def get_slug_validators(min_username_length, max_username_length, min_slug_length, max_slug_length, allow_letters_after_digits):
    return [
        generate_regex_validator(allow_dashes=True, allow_letters_after_digits=allow_letters_after_digits),
        reserved_username_validator,
        UsernameMinLengthValidator(limit_value=min_username_length),
        UsernameMaxLengthValidator(limit_value=max_username_length),
        SlugMinLengthValidator(limit_value=min_slug_length),
        SlugMaxLengthValidator(limit_value=max_slug_length),
        MinLengthValidator(limit_value=min_slug_length),
        MaxLengthValidator(limit_value=max_slug_length),
    ]


class ValidateUserPasswordMixin(object):
    def validate_password(self, password):
        from .models import User
        if len(password) < User.MIN_PASSWORD_LENGTH:
            raise ValidationError(_('Password too short.'))
        if len(password) > User.MAX_PASSWORD_LENGTH:
            raise ValidationError(_('Password too long.'))


