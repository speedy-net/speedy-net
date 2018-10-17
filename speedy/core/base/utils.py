import re
import random
import string

from datetime import date

from dateutil.relativedelta import relativedelta


# ~~~~ TODO: move to settings.
REGULAR_UDID_LENGTH = 20
SMALL_UDID_LENGTH = 15


def _generate_udid(length):
    digits = string.digits
    digits_without_zero = digits[1:]
    return ''.join(random.choice(digits if (i > 0) else digits_without_zero) for i in range(length))


def generate_regular_udid():
    return _generate_udid(length=REGULAR_UDID_LENGTH)


def generate_small_udid():
    return _generate_udid(length=SMALL_UDID_LENGTH)


# Export generate_regular_udid as generate_confirmation_token.
generate_confirmation_token = generate_regular_udid


def normalize_slug(slug):
    slug = slug.lower()
    slug = re.sub('[^a-zA-Z0-9]{1,}', '-', slug)
    slug = re.sub('^-', '', slug)
    slug = re.sub('-$', '', slug)
    return slug


def normalize_username(slug):
    slug = normalize_slug(slug=slug)
    username = re.sub('[-._]', '', slug)
    return username


def get_age(date_of_birth):
    today = date.today()
    age = today.year - date_of_birth.year
    if ((today.month, today.day) < (date_of_birth.month, date_of_birth.day)):
        age -= 1
    return age


def get_age_ranges_match(min_age, max_age):
    today = date.today()
    min_date = today - relativedelta(years=min_age)
    max_date = today - relativedelta(years=max_age + 1) + relativedelta(days=1)
    return max_date, min_date


def reflection_import(name):
    components = name.rsplit('.', maxsplit=2)
    mod = __import__(components[0], fromlist=[components[-2]])
    mod = getattr(mod, components[-2])
    klass = getattr(mod, components[-1])
    return klass


