import logging
from PIL import Image

from django.conf import settings as django_settings
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from speedy.core.base.utils import string_is_not_empty, string_is_not_none
from django.utils.translation import gettext_lazy as _, ngettext_lazy
from django.utils.timezone import now
from django.template.loader import render_to_string

from speedy.core.base.utils import normalize_slug, normalize_username, get_age_or_default, is_transparent

logger = logging.getLogger(__name__)


def reserved_username_validator(value):
    from .models import Entity
    if (normalize_username(username=value) in [normalize_username(username=reserved_username) for reserved_username in Entity.settings.RESERVED_USERNAMES]):
        raise ValidationError(_('This username is already taken.'))


def generate_regex_validator(allow_dashes, allow_letters_after_digits):
    letters = r'a-z'
    digits = r'0-9'
    letters_regex = r'[' + letters + r']'
    if (allow_dashes):
        symbols = r'\-'
        symbols_regex = r'[' + symbols + r']{0,1}'
    else:
        symbols = r''
        symbols_regex = r''
    digits_and_symbols_regex = r'[' + digits + symbols + r']'
    regex = r'(' + letters_regex + symbols_regex + r'){4,}' + digits_and_symbols_regex + r'*'
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
        return len(normalize_username(username=x))


class UsernameMaxLengthValidator(MaxLengthValidator):
    message = ngettext_lazy(
        singular='Username must contain at most %(limit_value)d alphanumeric character (it has %(show_value)d).',
        plural='Username must contain at most %(limit_value)d alphanumeric characters (it has %(show_value)d).',
        number='limit_value',
    )

    def clean(self, x):
        return len(normalize_username(username=x))


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

    def __init__(self, min_length=None):
        if (min_length is None):
            from .models import User
            min_length = User.settings.MIN_PASSWORD_LENGTH
        self.min_length = min_length

    def validate(self, password, user=None):
        if (len(password) < self.min_length):
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

    def __init__(self, max_length=None):
        if (max_length is None):
            from .models import User
            max_length = User.settings.MAX_PASSWORD_LENGTH
        self.max_length = max_length

    def validate(self, password, user=None):
        if (len(password) > self.max_length):
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
    from .models import User
    return (age in User.AGE_VALID_VALUES_IN_MODEL)


def age_is_valid_in_forms(age):
    from .models import User
    return (age in User.AGE_VALID_VALUES_IN_FORMS)


def validate_first_name_in_model(first_name):
    if (not (string_is_not_empty(first_name))):
        if (first_name is None):
            raise ValidationError(_('This field cannot be null.'))
        else:
            raise ValidationError(_('This field cannot be blank.'))


def validate_last_name_in_model(last_name):
    if (not (string_is_not_none(last_name))):
        raise ValidationError(_('This field cannot be null.'))


def validate_date_of_birth_in_model(date_of_birth):
    age = get_age_or_default(date_of_birth=date_of_birth)
    if (not (age_is_valid_in_model(age=age))):
        logger.debug("validate_date_of_birth_in_model::age is not valid in model (date_of_birth={date_of_birth}, age={age})".format(date_of_birth=date_of_birth, age=age))
        raise ValidationError(_('Enter a valid date.'))


def validate_date_of_birth_in_forms(date_of_birth):
    age = get_age_or_default(date_of_birth=date_of_birth)
    if (not (age_is_valid_in_forms(age=age))):
        logger.debug("validate_date_of_birth_in_forms::age is not valid in forms (date_of_birth={date_of_birth}, age={age})".format(date_of_birth=date_of_birth, age=age))
        raise ValidationError(_('Enter a valid date.'))


def validate_email_unique(email, user_email_address_pk=None):
    from .models import UserEmailAddress
    if (UserEmailAddress.objects.filter(email=email).exclude(pk=user_email_address_pk).exists()):
        # If this email address is not confirmed, delete it. Maybe another user added it but it belongs to the current user.
        for user_email_address in UserEmailAddress.objects.filter(email=email, is_confirmed=False).exclude(pk=user_email_address_pk):
            user_email_address.delete()
        # If this email address is confirmed, raise an exception.
        if (UserEmailAddress.objects.filter(email=email).exclude(pk=user_email_address_pk).exists()):
            raise ValidationError(_('This email is already in use.'))


def validate_profile_picture(profile_picture):
    if (not (profile_picture)):
        raise ValidationError(_("A profile picture is required."))
    if (profile_picture.size > django_settings.MAX_PHOTO_SIZE):
        raise ValidationError(_("This picture's file size is too big. The maximal file size allowed is 15 MB."))


def validate_profile_picture_for_user(user, profile_picture, test_new_profile_picture):
    validate_profile_picture(profile_picture=profile_picture)
    if (test_new_profile_picture):
        user._photo = user.photo
    photo_is_valid = False
    photo_is_invalid_reason = None
    try:
        if (test_new_profile_picture):
            user.photo = user._new_profile_picture

        profile_picture_html = render_to_string(template_name="accounts/tests/profile_picture_test.html", context={"user": user})
        logger.debug('validate_profile_picture_for_user::user={user}, profile_picture_html={profile_picture_html}'.format(
            user=user,
            profile_picture_html=profile_picture_html,
        ))
        if (not ('speedy-core/images/user.svg' in profile_picture_html)):
            with Image.open(user.photo.file) as image:
                if (getattr(image, "is_animated", False)):
                    photo_is_valid = False
                else:
                    photo_is_valid = True

        if (photo_is_valid):
            with Image.open(user.photo.file) as image:
                if (is_transparent(image)):
                    photo_is_valid = False
                    photo_is_invalid_reason = _("Please upload a nontransparent image.")
    except Exception as e:
        photo_is_valid = False
        logger.error('validate_profile_picture_for_user::user={user}, Exception={e} (registered {registered_days_ago} days ago)'.format(
            user=user,
            e=str(e),
            registered_days_ago=(now() - user.date_created).days,
        ))
    if (test_new_profile_picture):
        user.photo = user._photo
    if (not (photo_is_valid)):
        if (photo_is_invalid_reason):
            raise ValidationError(photo_is_invalid_reason)
        raise ValidationError(_("You can't use this format for your profile picture. Only JPEG or PNG formats are accepted."))


