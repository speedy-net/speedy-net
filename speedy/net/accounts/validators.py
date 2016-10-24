from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _

MIN_USERNAME_LENGTH = 6
MAX_USERNAME_LENGTH = 120



def reserved_username_validator(value):
    if value in settings.UNAVAILABLE_USERNAMES:
        raise ValidationError(_('This username is already taken.'))


username_validators = [
    validators.RegexValidator(regex=r'^([a-z]{4,}[0-9]{0,})$', message=_(
        'Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.')),
    validators.MinLengthValidator(MIN_USERNAME_LENGTH),
    validators.MaxLengthValidator(MAX_USERNAME_LENGTH),
    reserved_username_validator,
]

slug_validators = [
    validators.RegexValidator(regex=r'^([a-z\-\._]{4,}[0-9\-\._]{0,})$', message=_(
        'Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.')),
    validators.MinLengthValidator(MIN_USERNAME_LENGTH),
    validators.MaxLengthValidator(MAX_USERNAME_LENGTH),
    reserved_username_validator,
]
