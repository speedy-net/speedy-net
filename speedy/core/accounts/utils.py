from django.apps import apps
from django.conf import settings as django_settings


def get_site_profile_model(profile_model=None):
    """
    Get the site profile model.

    :param profile_model: The profile model.
    :type profile_model: str or None
    :return: The site profile model.
    :rtype django.db.models.Model
    """
    if (not (profile_model)):
        profile_model = django_settings.AUTH_SITE_PROFILE_MODEL
    return apps.get_model(*profile_model.split('.'))


def normalize_email(email):
    """
    Normalize the email address by lowercasing it.

    :param email: The email address.
    :type email: str
    :return: The normalized email address.
    :rtype str
    """
    from .models import User
    email = User.objects.normalize_email(email=email)
    email = email.lower()
    return email


