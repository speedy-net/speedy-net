import uuid
import hashlib
import os
from django.core import validators

INITIAL_MAX_ID = 1000000000000000

def generate_id(number_limit=INITIAL_MAX_ID):
    """ generate unique UUID, convert to number and limit """
    return uuid.uuid4().int % number_limit


def generate_token():
    return hashlib.sha512(os.urandom(128)).hexdigest()
