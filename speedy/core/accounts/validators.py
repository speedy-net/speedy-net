"""
Validators of the Speedy Core accounts app for usernames, slugs, passwords, ages, dates of birth and profile pictures.
"""
import logging
from datetime import timedelta
from PIL import Image

from django.conf import settings as django_settings
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from speedy.core.base.utils import string_is_not_empty, string_is_not_none
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _, ngettext_lazy, pgettext_lazy
from django.template.loader import render_to_string

from speedy.core.base.utils import normalize_slug, normalize_username, get_age_or_default, is_animated, is_transparent

logger = logging.getLogger(__name__)


def reserved_username_validator(value):
    """
    Validates that the given value is not one of the reserved usernames.

    :param value: The username to validate.
    :type value: str
    :raises django.core.exceptions.ValidationError: If the normalized value matches a reserved username.
    """
    from .models import Entity
    if (normalize_username(username=value) in [normalize_username(username=reserved_username) for reserved_username in Entity.settings.RESERVED_USERNAMES]):
        raise ValidationError(_('This username is already taken.'))


def generate_regex_validator(allow_dashes, allow_letters_after_digits):
    """
    Builds a :class:`~django.core.validators.RegexValidator` for usernames or slugs, based on whether dashes and letters after digits are allowed.

    :param allow_dashes: Whether dashes are allowed in the value (True for slugs, False for usernames).
    :type allow_dashes: bool
    :param allow_letters_after_digits: Whether letters are allowed to appear after digits.
    :type allow_letters_after_digits: bool
    :return: A regex validator matching the generated pattern, with an appropriate error message.
    :rtype: django.core.validators.RegexValidator
    """
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
    """
    Validates that a username has at least a minimum number of alphanumeric characters, after normalizing it (ignoring dashes).
    """

    message = ngettext_lazy(
        singular='Username must contain at least %(limit_value)d alphanumeric character (it has %(show_value)d).',
        plural='Username must contain at least %(limit_value)d alphanumeric characters (it has %(show_value)d).',
        number='limit_value',
    )

    def clean(self, x):
        """
        Returns the length of the normalized username, used by the base validator to compare against the limit value.

        :param x: The username to normalize and measure.
        :type x: str
        :return: The length of the normalized username.
        :rtype: int
        """
        return len(normalize_username(username=x))


class UsernameMaxLengthValidator(MaxLengthValidator):
    """
    Validates that a username has at most a maximum number of alphanumeric characters, after normalizing it (ignoring dashes).
    """

    message = ngettext_lazy(
        singular='Username must contain at most %(limit_value)d alphanumeric character (it has %(show_value)d).',
        plural='Username must contain at most %(limit_value)d alphanumeric characters (it has %(show_value)d).',
        number='limit_value',
    )

    def clean(self, x):
        """
        Returns the length of the normalized username, used by the base validator to compare against the limit value.

        :param x: The username to normalize and measure.
        :type x: str
        :return: The length of the normalized username.
        :rtype: int
        """
        return len(normalize_username(username=x))


class SlugMinLengthValidator(MinLengthValidator):
    """
    Validates that a slug has at least a minimum number of characters, after normalizing it (including dashes).
    """

    message = ngettext_lazy(
        singular='Username must contain at least %(limit_value)d character (it has %(show_value)d).',
        plural='Username must contain at least %(limit_value)d characters (it has %(show_value)d).',
        number='limit_value',
    )

    def clean(self, x):
        """
        Returns the length of the normalized slug, used by the base validator to compare against the limit value.

        :param x: The slug to normalize and measure.
        :type x: str
        :return: The length of the normalized slug.
        :rtype: int
        """
        return len(normalize_slug(slug=x))


class SlugMaxLengthValidator(MaxLengthValidator):
    """
    Validates that a slug has at most a maximum number of characters, after normalizing it (including dashes).
    """

    message = ngettext_lazy(
        singular='Username must contain at most %(limit_value)d character (it has %(show_value)d).',
        plural='Username must contain at most %(limit_value)d characters (it has %(show_value)d).',
        number='limit_value',
    )

    def clean(self, x):
        """
        Returns the length of the normalized slug, used by the base validator to compare against the limit value.

        :param x: The slug to normalize and measure.
        :type x: str
        :return: The length of the normalized slug.
        :rtype: int
        """
        return len(normalize_slug(slug=x))


class PasswordMinLengthValidator:
    """
    Validate whether the password is of a minimum length.

    Attributes:
        min_length (int): The minimum number of characters a password must contain.

    Methods:
        __init__(self, min_length=None): Sets the minimum length, defaulting to ``User.settings.MIN_PASSWORD_LENGTH``.
        validate(self, password, user=None): Raises a :class:`~django.core.exceptions.ValidationError` if the password is shorter than the minimum length.
        get_help_text(self): Returns a help text describing the minimum length requirement.
    """

    def __init__(self, min_length=None):
        """
        Sets the minimum password length.

        :param min_length: The minimum number of characters a password must contain. If None, defaults to ``User.settings.MIN_PASSWORD_LENGTH``.
        :type min_length: int or None
        """
        if (min_length is None):
            from .models import User
            min_length = User.settings.MIN_PASSWORD_LENGTH
        self.min_length = min_length

    def validate(self, password, user=None):
        """
        Validates that the password contains at least the minimum number of characters.

        :param password: The password to validate.
        :type password: str
        :param user: The user the password is being validated for, if any. Unused.
        :type user: speedy.core.accounts.models.User or None
        :raises django.core.exceptions.ValidationError: If the password is shorter than the minimum length.
        """
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
        """
        Returns a help text describing the minimum password length requirement.

        :return: The help text.
        :rtype: str
        """
        return ngettext_lazy(
            singular="Your password must contain at least %(min_length)d character.",
            plural="Your password must contain at least %(min_length)d characters.",
            number=self.min_length,
        ) % {'min_length': self.min_length}


class PasswordMaxLengthValidator:
    """
    Validate whether the password is of a maximum length.

    Attributes:
        max_length (int): The maximum number of characters a password may contain.

    Methods:
        __init__(self, max_length=None): Sets the maximum length, defaulting to ``User.settings.MAX_PASSWORD_LENGTH``.
        validate(self, password, user=None): Raises a :class:`~django.core.exceptions.ValidationError` if the password is longer than the maximum length.
        get_help_text(self): Returns a help text describing the maximum length requirement.
    """

    def __init__(self, max_length=None):
        """
        Sets the maximum password length.

        :param max_length: The maximum number of characters a password may contain. If None, defaults to ``User.settings.MAX_PASSWORD_LENGTH``.
        :type max_length: int or None
        """
        if (max_length is None):
            from .models import User
            max_length = User.settings.MAX_PASSWORD_LENGTH
        self.max_length = max_length

    def validate(self, password, user=None):
        """
        Validates that the password contains at most the maximum number of characters.

        :param password: The password to validate.
        :type password: str
        :param user: The user the password is being validated for, if any. Unused.
        :type user: speedy.core.accounts.models.User or None
        :raises django.core.exceptions.ValidationError: If the password is longer than the maximum length.
        """
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
        """
        Returns a help text describing the maximum password length requirement.

        :return: The help text.
        :rtype: str
        """
        return ngettext_lazy(
            singular="Your password must contain at most %(max_length)d character.",
            plural="Your password must contain at most %(max_length)d characters.",
            number=self.max_length,
        ) % {'max_length': self.max_length}


class PasswordMinUniqueCharsValidator:
    """
    Validate whether the password contains a minimum of unique characters.

    Attributes:
        min_unique_characters (int): The minimum number of distinct characters a password must contain.

    Methods:
        __init__(self, min_unique_characters=None): Sets the minimum unique characters, defaulting to ``User.settings.MIN_PASSWORD_UNIQUE_CHARACTERS``.
        validate(self, password, user=None): Raises a :class:`~django.core.exceptions.ValidationError` if the password has fewer unique characters than required.
        get_help_text(self): Returns a help text describing the minimum unique characters requirement.
    """

    def __init__(self, min_unique_characters=None):
        """
        Sets the minimum number of unique characters required in the password.

        :param min_unique_characters: The minimum number of distinct characters a password must contain. If None, defaults to ``User.settings.MIN_PASSWORD_UNIQUE_CHARACTERS``.
        :type min_unique_characters: int or None
        """
        if (min_unique_characters is None):
            from .models import User
            min_unique_characters = User.settings.MIN_PASSWORD_UNIQUE_CHARACTERS
        self.min_unique_characters = min_unique_characters

    def validate(self, password, user=None):
        """
        Validates that the password contains at least the minimum number of unique characters.

        :param password: The password to validate.
        :type password: str
        :param user: The user the password is being validated for, if any. Unused.
        :type user: speedy.core.accounts.models.User or None
        :raises django.core.exceptions.ValidationError: If the password has fewer unique characters than required.
        """
        if (len(set(list(password))) < self.min_unique_characters):
            raise ValidationError(
                _("Your password must contain at least %(min_unique_characters)d unique characters.") % {'min_unique_characters': self.min_unique_characters},
                code='password_unique_characters_too_little',
            )

    def get_help_text(self):
        """
        Returns a help text describing the minimum unique characters requirement.

        :return: The help text.
        :rtype: str
        """
        return _("Your password must contain at least %(min_unique_characters)d unique characters.") % {'min_unique_characters': self.min_unique_characters}


def get_username_validators(min_username_length, max_username_length, allow_letters_after_digits):
    """
    Builds the list of validators applied to a username field.

    :param min_username_length: The minimum allowed username length.
    :type min_username_length: int
    :param max_username_length: The maximum allowed username length.
    :type max_username_length: int
    :param allow_letters_after_digits: Whether letters are allowed to appear after digits in the username.
    :type allow_letters_after_digits: bool
    :return: A list of validators to run against the username.
    :rtype: list
    """
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
    """
    Builds the list of validators applied to a slug field.

    :param min_username_length: The minimum allowed username length (used for the username-length checks on the slug).
    :type min_username_length: int
    :param max_username_length: The maximum allowed username length (used for the username-length checks on the slug).
    :type max_username_length: int
    :param min_slug_length: The minimum allowed slug length.
    :type min_slug_length: int
    :param max_slug_length: The maximum allowed slug length.
    :type max_slug_length: int
    :param allow_letters_after_digits: Whether letters are allowed to appear after digits in the slug.
    :type allow_letters_after_digits: bool
    :return: A list of validators to run against the slug.
    :rtype: list
    """
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
    """
    Checks whether an age value is one of the valid ages allowed in the model.

    :param age: The age value.
    :type age: int or None
    :return: True if the age is valid, False otherwise.
    :rtype: bool
    """
    from .models import User
    return (age in User.AGE_VALID_VALUES_IN_MODEL)


def age_is_valid_in_forms(age):
    """
    Checks whether an age value is one of the valid ages allowed in forms.

    :param age: The age value.
    :type age: int or None
    :return: True if the age is valid, False otherwise.
    :rtype: bool
    """
    from .models import User
    return (age in User.AGE_VALID_VALUES_IN_FORMS)


def validate_first_name_in_model(first_name):
    """
    Validates that the first name is not empty or null, when saved on the model.

    :param first_name: The first name to validate.
    :type first_name: str or None
    :raises django.core.exceptions.ValidationError: If the first name is null or blank.
    """
    if (not (string_is_not_empty(s=first_name))):
        if (first_name is None):
            raise ValidationError(_('This field cannot be null.'))
        else:
            raise ValidationError(_('This field cannot be blank.'))


def validate_last_name_in_model(last_name):
    """
    Validates that the last name is not null, when saved on the model. Unlike the first name, the last name may be blank.

    :param last_name: The last name to validate.
    :type last_name: str or None
    :raises django.core.exceptions.ValidationError: If the last name is null.
    """
    if (not (string_is_not_none(s=last_name))):
        raise ValidationError(_('This field cannot be null.'))


def validate_date_of_birth_in_model(date_of_birth):
    """
    Validates that the date of birth results in an age that is valid in the model.

    :param date_of_birth: The date of birth to validate.
    :type date_of_birth: datetime.date or None
    :raises django.core.exceptions.ValidationError: If the resulting age is not valid in the model.
    """
    age = get_age_or_default(date_of_birth=date_of_birth)
    if (not (age_is_valid_in_model(age=age))):
        logger.debug("validate_date_of_birth_in_model::age is not valid in model (date_of_birth={date_of_birth}, age={age})".format(date_of_birth=date_of_birth, age=age))
        raise ValidationError(_('Enter a valid date.'))


def validate_date_of_birth_in_forms(date_of_birth):
    """
    Validates that the date of birth results in an age that is valid in forms.

    :param date_of_birth: The date of birth to validate.
    :type date_of_birth: datetime.date or None
    :raises django.core.exceptions.ValidationError: If the resulting age is not valid in forms.
    """
    age = get_age_or_default(date_of_birth=date_of_birth)
    if (not (age_is_valid_in_forms(age=age))):
        logger.debug("validate_date_of_birth_in_forms::age is not valid in forms (date_of_birth={date_of_birth}, age={age})".format(date_of_birth=date_of_birth, age=age))
        raise ValidationError(_('Enter a valid date.'))


def validate_email_unique(email, user_email_address_pk=None):
    """
    Validates that the email address is not already in use by another user. Unconfirmed email addresses of other users that were created at least 5 minutes ago are deleted, to free them up for the current user, rather than treating them as a conflict.

    :param email: The email address to validate.
    :type email: str
    :param user_email_address_pk: The primary key of the email address being validated (if it already exists), excluded from the uniqueness check.
    :type user_email_address_pk: int or None
    :raises django.core.exceptions.ValidationError: If the email address is already in use by another, confirmed or recently created, email address.
    """
    from .models import UserEmailAddress
    if (UserEmailAddress.objects.filter(email=email).exclude(pk=user_email_address_pk).exists()):
        # If this email address is not confirmed, delete it. Maybe another user added it but it belongs to the current user.
        for user_email_address in UserEmailAddress.objects.filter(email=email, is_confirmed=False).exclude(pk=user_email_address_pk):
            # Only delete this email address if it was created at least 5 minutes ago.
            if (user_email_address.date_created <= (now() - timedelta(minutes=5))):
                user_email_address.delete()
        # If this email address is confirmed or was created less than 5 minutes ago, raise an exception.
        if (UserEmailAddress.objects.filter(email=email).exclude(pk=user_email_address_pk).exists()):
            raise ValidationError(_('This email is already in use.'))


def validate_image_file_extension(value):
    """
    Validates that the given file has one of the allowed image file extensions.

    :param value: The file to validate.
    :type value: django.core.files.File
    :return: The result of running the configured :class:`~django.core.validators.FileExtensionValidator` on the file.
    :rtype: None
    :raises django.core.exceptions.ValidationError: If the file's extension is not allowed.
    """
    return FileExtensionValidator(allowed_extensions=django_settings.IMAGE_FILE_EXTENSIONS)(value=value)


def validate_profile_picture(profile_picture):
    """
    Validates that a profile picture is provided and that its file size does not exceed the maximum allowed size.

    :param profile_picture: The profile picture to validate.
    :type profile_picture: django.core.files.File or None
    :raises django.core.exceptions.ValidationError: If the profile picture is missing, or its file size is too big.
    """
    if (not (profile_picture)):
        raise ValidationError(_("A profile picture is required."))
    if (profile_picture.size > django_settings.MAX_PHOTO_SIZE):
        raise ValidationError(_("This picture's file size is too big. The maximal file size allowed is 30 MB."))


def validate_profile_picture_for_user(user, profile_picture, test_new_profile_picture):
    """
    Validates a profile picture for a specific user, in addition to the basic validation (presence and file size). Renders the user's profile picture template to check whether the image is animated or transparent, neither of which is allowed, logging and raising a validation error for the user's gender if that is the case.

    :param user: The user the profile picture belongs to (or is being tested for).
    :type user: speedy.core.accounts.models.User
    :param profile_picture: The profile picture to validate.
    :type profile_picture: django.core.files.File or None
    :param test_new_profile_picture: If True, temporarily sets ``user.photo`` to ``user._new_profile_picture`` while validating, then restores it.
    :type test_new_profile_picture: bool
    :raises django.core.exceptions.ValidationError: If the profile picture is missing, too big, animated, or transparent.
    """
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
            with user.photo.file, Image.open(user.photo.file) as image:
                if (is_animated(image=image)):
                    photo_is_valid = False
                    photo_is_invalid_reason = _("You can't use this format for your profile picture. Only JPEG or PNG formats are accepted.")
                elif (is_transparent(image=image)):
                    photo_is_valid = False
                    photo_is_invalid_reason = pgettext_lazy(context=user.get_gender(), message="Your profile picture can't be transparent. Please upload a nontransparent image.")
                else:
                    photo_is_valid = True
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
        if (photo_is_invalid_reason is not None):
            raise ValidationError(photo_is_invalid_reason)
        else:
            raise ValidationError(_("You can't use this format for your profile picture. Only JPEG or PNG formats are accepted."))


