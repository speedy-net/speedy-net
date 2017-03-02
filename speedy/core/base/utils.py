import re
import random
import string
import datetime


REGULAR_UDID_LENGTH = 20
SMALL_UDID_LENGTH = 15


def _generate_udid(length):
    digits = string.digits
    digits_without_zero = digits[1:]
    return ''.join(random.choice(digits if i > 0 else digits_without_zero) for i in range(length))


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
    username = re.sub('[-\._]', '', slug)
    return username


def get_age(date_birth):
    today = datetime.datetime.today()
    return today.year - date_birth.year - int((today.month, today.day) < (date_birth.month, date_birth.day))
