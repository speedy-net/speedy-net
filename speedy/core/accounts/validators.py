import logging

from django.conf import settings
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.utils.translation import gettext_lazy as _, ngettext_lazy

from speedy.core.base.utils import normalize_slug, normalize_username, _get_age_or_default


log = logging.getLogger(__name__)


def reserved_username_validator(value):
    if (normalize_username(slug=value) in [normalize_username(slug=reserved) for reserved in settings.UNAVAILABLE_USERNAMES]):
        raise ValidationError(_('This username is already taken.'))


def generate_regex_validator(allow_dashes, allow_letters_after_digits):
    letters = r'a-z'
    digits = r'0-9'
    symbols = r'\-' if (allow_dashes) else r''
    regex = r'[' + letters + symbols + ']{4,}[' + digits + symbols + ']*'
    if (allow_letters_after_digits):
        regex += r'[' + letters + digits + symbols + ']*'
    if (allow_letters_after_digits):
        invalid_regex_message = _("Username must start with 4 or more letters, and may contain letters, digits or dashes.")
    else:
        invalid_regex_message = _("Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.")
    return RegexValidator(regex=r'^(' + regex + ')$', message=invalid_regex_message)


class UsernameMinLengthValidator(MinLengthValidator):
    message = ngettext_lazy(
        singular='Username must contain at least %(limit_value)d alphanumeric character (it has %(show_value)d).',
        plural='Username must contain at least %(limit_value)d alphanumeric characters (it has %(show_value)d).',
        number='limit_value',
    )

    def clean(self, x):
        return len(normalize_username(slug=x))


class UsernameMaxLengthValidator(MaxLengthValidator):
    message = ngettext_lazy(
        singular='Username must contain at most %(limit_value)d alphanumeric character (it has %(show_value)d).',
        plural='Username must contain at most %(limit_value)d alphanumeric characters (it has %(show_value)d).',
        number='limit_value',
    )

    def clean(self, x):
        return len(normalize_username(slug=x))


class SlugMinLengthValidator(MinLengthValidator):
    message = ngettext_lazy(
        singular='Username must contain at least %(limit_value)d character (it has %(show_value)d).',
        plural='Username must contain at least %(limit_value)d characters (it has %(show_value)d).',
        number='limit_value',
    )

    def clean(self, x):
        return len(normalize_slug(slug=x))


class SlugMaxLengthValidator(MaxLengthValidator):
    message = ngettext_lazy(
        singular='Username must contain at most %(limit_value)d character (it has %(show_value)d).',
        plural='Username must contain at most %(limit_value)d characters (it has %(show_value)d).',
        number='limit_value',
    )

    def clean(self, x):
        return len(normalize_slug(slug=x))


class PasswordMinLengthValidator:
    """
    Validate whether the password is of a minimum length.
    """
    def __init__(self, min_length=settings.MIN_PASSWORD_LENGTH):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                ngettext_lazy(
                    singular="This password is too short. It must contain at least %(min_length)d character.",
                    plural="This password is too short. It must contain at least %(min_length)d characters.",
                    number=self.min_length,
                ),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return ngettext_lazy(
            singular="Your password must contain at least %(min_length)d character.",
            plural="Your password must contain at least %(min_length)d characters.",
            number=self.min_length,
        ) % {'min_length': self.min_length}


class PasswordMaxLengthValidator:
    """
    Validate whether the password is of a maximum length.
    """
    def __init__(self, max_length=settings.MAX_PASSWORD_LENGTH):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                ngettext_lazy(
                    singular="This password is too long. It must contain at most %(max_length)d character.",
                    plural="This password is too long. It must contain at most %(max_length)d characters.",
                    number=self.max_length,
                ),
                code='password_too_long',
                params={'max_length': self.max_length},
            )

    def get_help_text(self):
        return ngettext_lazy(
            singular="Your password must contain at most %(max_length)d character.",
            plural="Your password must contain at most %(max_length)d characters.",
            number=self.max_length,
        ) % {'max_length': self.max_length}


def get_username_validators(min_username_length, max_username_length, allow_letters_after_digits):
    return [
        generate_regex_validator(allow_dashes=False, allow_letters_after_digits=allow_letters_after_digits),
        UsernameMinLengthValidator(limit_value=min_username_length),
        UsernameMaxLengthValidator(limit_value=max_username_length),
        SlugMinLengthValidator(limit_value=min_username_length),
        SlugMaxLengthValidator(limit_value=max_username_length),
        MinLengthValidator(limit_value=min_username_length),
        MaxLengthValidator(limit_value=max_username_length),
        reserved_username_validator,
    ]


def get_slug_validators(min_username_length, max_username_length, min_slug_length, max_slug_length, allow_letters_after_digits):
    return [
        generate_regex_validator(allow_dashes=True, allow_letters_after_digits=allow_letters_after_digits),
        UsernameMinLengthValidator(limit_value=min_username_length),
        UsernameMaxLengthValidator(limit_value=max_username_length),
        SlugMinLengthValidator(limit_value=min_slug_length),
        SlugMaxLengthValidator(limit_value=max_slug_length),
        MinLengthValidator(limit_value=min_slug_length),
        MaxLengthValidator(limit_value=max_slug_length),
        reserved_username_validator,
    ]


def age_is_valid_in_model(age):
    from .models import User # ~~~~ TODO
    return (age in User.AGE_VALID_VALUES_IN_MODEL)


def age_is_valid_in_forms(age):
    from .models import User # ~~~~ TODO
    return (age in User.AGE_VALID_VALUES_IN_FORMS)


# ~~~~ TODO: create tests for this validator.
def validate_date_of_birth_in_model(date_of_birth):
    age = _get_age_or_default(date_of_birth=date_of_birth)
    if (not (age_is_valid_in_model(age=age))):
        log.debug("validate_date_of_birth_in_model::age is not valid in model (date_of_birth={date_of_birth}, age={age})".format(date_of_birth=date_of_birth, age=age))
        raise ValidationError(_('Enter a valid date.'))
        # raise ValidationError(_('Enter a valid date (age can be from 0 to 250 years).')) #### TODO


# ~~~~ TODO: create tests for this validator.
def validate_date_of_birth_in_forms(date_of_birth):
    age = _get_age_or_default(date_of_birth=date_of_birth)
    if (not (age_is_valid_in_forms(age=age))):
        log.debug("validate_date_of_birth_in_forms::age is not valid in forms (date_of_birth={date_of_birth}, age={age})".format(date_of_birth=date_of_birth, age=age))
        raise ValidationError(_('Enter a valid date.'))
        # raise ValidationError(_('Enter a valid date (age can be from 0 to 180 years).')) #### TODO


class ValidateUserPasswordMixin(object):
    def validate_password(self, password):
        password_validation.validate_password(password=password)


