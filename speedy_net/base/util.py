# import uuid
import hashlib
import os
import random
from django.core import validators


def generate_id():
    """ generate unique UUID, convert to number and limit """
    return "{}".format(random.randint(100000000000000, 999999999999999))


def generate_token():
    return hashlib.sha512(os.urandom(128)).hexdigest()
