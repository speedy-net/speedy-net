import sys

from django.conf import settings as django_settings


def patch():
    """
    Patch modules in test-requirements.txt to not break if imported when TESTS = False.
    """
    if (not(django_settings.TESTS)):
        sys.modules.setdefault('factory', SimpleMagicMock())


def _is_magic(name):
    return '__%s__' % name[2:-2] == name


class SimpleMagicMock(object):
    """
    Bare-bones implementation of unittest.mock.MagicMock.
    """
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, name):
        if _is_magic(name):
            raise AttributeError(name)
        return self
