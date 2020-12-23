import logging
import re
import random
import string

from datetime import date
from dateutil.relativedelta import relativedelta

from django.conf import settings as django_settings
from django.utils import translation
from django.utils.translation import get_language

import translated_fields

logger = logging.getLogger(__name__)


def _generate_udid(length):
    digits = string.digits
    digits_without_zero = digits[1:]
    return ''.join(random.choice(digits if (i > 0) else digits_without_zero) for i in range(length))


def generate_small_udid():
    return _generate_udid(length=django_settings.SMALL_UDID_LENGTH)


def generate_regular_udid():
    return _generate_udid(length=django_settings.REGULAR_UDID_LENGTH)


# Export generate_regular_udid as generate_confirmation_token.
generate_confirmation_token = generate_regular_udid


def normalize_slug(slug):
    """
    Normalize the slug.
    """
    slug = slug.lower()
    slug = re.sub('[^a-zA-Z0-9]{1,}', '-', slug)
    slug = re.sub('^-', '', slug)
    slug = re.sub('-$', '', slug)
    return slug


def normalize_username(username):
    """
    Normalize the username.
    """
    slug = normalize_slug(slug=username)
    username = re.sub('[-._]', '', slug)
    return username


def get_age(date_of_birth):
    today = date.today()
    age = today.year - date_of_birth.year
    if ((today.month, today.day) < (date_of_birth.month, date_of_birth.day)):
        age -= 1
    return age


def get_age_or_default(date_of_birth, default=-9 * (10 ** 15)):
    try:
        age = get_age(date_of_birth=date_of_birth)
    except AttributeError:
        age = default
    return age


def get_age_ranges_match(min_age, max_age):
    today = date.today()
    max_date = today - relativedelta(years=min_age)
    min_date = today - relativedelta(years=max_age + 1) + relativedelta(days=1)
    return min_date, max_date


def reflection_import(name):
    components = name.rsplit('.', maxsplit=2)
    mod = __import__(components[0], fromlist=[components[-2]])
    mod = getattr(mod, components[-2])
    klass = getattr(mod, components[-1])
    return klass


def string_is_not_empty(s):
    if (s in [None, ""]):
        return False
    if (isinstance(s, str)):
        return True
    return False


def string_is_not_none(s):
    if (s is None):
        return False
    if (isinstance(s, str)):
        return True
    return False


def to_attribute(name, language_code=None):
    language_code = language_code or get_language() or django_settings.LANGUAGE_CODE
    return translated_fields.to_attribute(name=name, language_code=language_code)


def get_all_field_names(base_field_name):
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
    assert (len(field_names) == 2)
    return field_names


def update_form_field_choices(field, choices):
    """
    Update both field.choices and field.widget.choices to the same value (list of choices).
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
    :type image: PIL.Image.Image
    """
    if ('transparency' in image.info):
        return True

    elif (image.mode == 'RGBA'):
        extrema = image.getextrema()
        if (extrema[3][0] < 255):
            return True

    return False
