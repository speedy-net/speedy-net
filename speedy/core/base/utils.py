import logging
import re
import secrets
import string

from datetime import date
from dateutil.relativedelta import relativedelta

from django.conf import settings as django_settings
from django.utils import translation
from django.utils.timesince import TIME_STRINGS as timesince_time_strings
from django.utils.html import avoid_wrapping
from django.utils.translation import pgettext, get_language

import translated_fields

logger = logging.getLogger(__name__)


def _generate_udid(length):
    """
    Generate a random udid.

    :param length: The length of the udid.
    :type length: int
    :return: The udid.
    :rtype str
    """
    digits = string.digits
    digits_without_zero = digits[1:]
    return ''.join(secrets.choice(digits if (i > 0) else digits_without_zero) for i in range(length))


def generate_small_udid():
    """
    Generate a small udid.

    :return: The udid.
    :rtype str
    """
    return _generate_udid(length=django_settings.SMALL_UDID_LENGTH)


def generate_regular_udid():
    """
    Generate a regular udid.

    :return: The udid.
    :rtype str
    """
    return _generate_udid(length=django_settings.REGULAR_UDID_LENGTH)


# Export generate_regular_udid as generate_confirmation_token.
generate_confirmation_token = generate_regular_udid


def normalize_slug(slug):
    """
    Normalize the slug.

    :param slug: The slug.
    :type slug: str
    :return: The normalized slug.
    :rtype str
    """
    slug = slug.lower()
    slug = re.sub(pattern=r'[^a-zA-Z0-9]{1,}', repl='-', string=slug)
    slug = re.sub(pattern=r'^-', repl='', string=slug)
    slug = re.sub(pattern=r'-$', repl='', string=slug)
    return slug


def normalize_username(username):
    """
    Normalize the username.

    :param username: The username.
    :type username: str
    :return: The normalized username.
    :rtype str
    """
    slug = normalize_slug(slug=username)
    username = re.sub(pattern=r'[-._]', repl='', string=slug)
    return username


def get_age(date_of_birth):
    """
    Get the age of the user.

    :param date_of_birth: The date of birth of the user.
    :type date_of_birth: datetime.date
    :return: The age of the user.
    :rtype int
    """
    today = date.today()
    age = today.year - date_of_birth.year
    if ((today.month, today.day) < (date_of_birth.month, date_of_birth.day)):
        age -= 1
    return age


def get_age_or_default(date_of_birth, default=-9 * (10 ** 15)):
    """
    Get the age of the user, or the default value if the date of birth is None.

    :param date_of_birth: The date of birth of the user.
    :type date_of_birth: datetime.date
    :param default: The default value.
    :type default: int
    :return: The age of the user.
    :rtype int
    """
    try:
        age = get_age(date_of_birth=date_of_birth)
    except AttributeError:
        age = default
    return age


def get_age_ranges_match(min_age, max_age):
    """
    Get the age ranges match.

    :param min_age: The minimum age.
    :type min_age: int
    :param max_age: The maximum age.
    :type max_age: int
    :return: The age ranges match.
    :rtype tuple
    """
    today = date.today()
    max_date = today - relativedelta(years=min_age)
    min_date = today - relativedelta(years=max_age + 1) + relativedelta(days=1)
    return min_date, max_date


def reflection_import(name):
    """
    Import a class by name.

    :param name: The name of the class.
    :type name: str
    :return: The class.
    :rtype type
    """
    components = name.rsplit('.', maxsplit=2)
    mod = __import__(components[0], fromlist=[components[-2]])
    mod = getattr(mod, components[-2])
    klass = getattr(mod, components[-1])
    return klass


def string_is_not_empty(s):
    """
    Check if the string is not empty.

    :param s: The string.
    :type s: str
    :return: True if the string is not empty, False otherwise.
    :rtype bool
    """
    if (s in [None, ""]):
        return False
    if (isinstance(s, str)):
        return True
    return False


def string_is_not_none(s):
    """
    Check if the string is not None.

    :param s: The string.
    :type s: str
    :return: True if the string is not None, False otherwise.
    :rtype bool
    """
    if (s is None):
        return False
    if (isinstance(s, str)):
        return True
    return False


def to_attribute(name, language_code=None):
    """
    Get the attribute name for the given language code.

    :param name: The name of the field.
    :type name: str
    :param language_code: The language code.
    :type language_code: str
    :return: The attribute name.
    :rtype str
    """
    language_code = language_code or get_language() or django_settings.LANGUAGE_CODE
    return translated_fields.to_attribute(name=name, language_code=language_code)


def get_all_field_names(base_field_name):
    """
    Get all field names for the given base field name.

    :param base_field_name: The base field name.
    :type base_field_name: str
    :return: The list of field names.
    :rtype list
    """
    field_names = []
    this_language_code = translation.get_language()
    all_other_language_codes = [language_code for language_code, language_name in django_settings.LANGUAGES if (not (language_code == this_language_code))]
    for language_code in [this_language_code] + all_other_language_codes:
        field_name_localized = to_attribute(name=base_field_name, language_code=language_code)
        field_names.append(field_name_localized)
    # logger.debug("get_all_field_names::this_language_code={this_language_code}, base_field_name={base_field_name}, field_names={field_names}".format(
    #     this_language_code=this_language_code,
    #     base_field_name=base_field_name,
    #     field_names=field_names,
    # ))
    assert (len(field_names) == 7)
    return field_names


def update_form_field_choices(field, choices):
    """
    Update both field.choices and field.widget.choices to the same value (list of choices).

    :param field: The form field.
    :type field: django.forms.Field
    :param choices: The list of choices.
    :type choices: list
    """
    field.choices = choices
    field.widget.choices = choices


def get_both_genders_context_from_genders(user_gender, other_user_gender):
    both_genders_context = "{}_{}".format(user_gender, other_user_gender)
    return both_genders_context


def get_both_genders_context_from_users(user, other_user):
    return get_both_genders_context_from_genders(user_gender=user.get_gender(), other_user_gender=other_user.get_gender())


def is_transparent(image):
    """
    Check if the image is transparent.

    :param image: The image.
    :type image: PIL.Image.Image
    :return: True if the image is transparent, False otherwise.
    :rtype bool
    """
    if ('transparency' in image.info):
        return True

    elif (image.mode == 'RGBA'):
        extrema = image.getextrema()
        if (extrema[3][0] < 255):
            return True

    elif (image.mode == 'LA'):
        extrema = image.getextrema()
        if (extrema[1][0] < 255):
            return True

    return False


def convert_to_set(exclude=None):
    """
    Convert the exclude list to a set. If exclude is None, return an empty set. If exclude is a set, return it as is.

    :param exclude: The list of items to exclude.
    :type exclude: list or set
    :return: The set.
    :rtype set
    """
    if (exclude is None):
        exclude = set()
    else:
        exclude = set(exclude)
    return exclude


def timesince(d, now):
    """
    Like Django's timesince but more accurate. Returns results only when delta is at least one day (positive). Otherwise returns "". Result is either one or two in depth.

    :param d: The date.
    :type d: datetime.datetime
    :param now: The current date.
    :type now: datetime.datetime
    :return: The timesince string.
    :rtype str
    """
    delta = -relativedelta(d, now)

    result = []
    if ((delta.years >= 0) and (delta.months >= 0) and (delta.days >= 0)):

        years = delta.years
        months = delta.months
        weeks = delta.days // 7
        days = delta.days - weeks * 7

        timesince_counts = [(years, "year"), (months, "month")]
        if (years == 0):
            timesince_counts.append((weeks, "week"))
            if (months == 0):
                timesince_counts.append((days, "day"))

        for (count, name) in timesince_counts:
            if (count > 0):
                result.append(avoid_wrapping(value=timesince_time_strings[name] % {"num": count}))

    result = pgettext(context="timesince", message=", ").join(result)
    if (get_language() == "he"):
        result = re.sub(pattern=r'(\ {1}ו{1})(\d{1})', repl=lambda m: "-".join(m.groups()), string=result)
    return result


