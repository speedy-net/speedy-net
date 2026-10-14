from django.conf import settings as django_settings
from django.db import migrations

from speedy.core.base.utils import to_attribute


def get_registration_site_id_and_language_code(user, profile):
    """
    Guess the site ID and the language code the user registered with, from the Speedy Match profile of the user.

    :param user: The user (historical model).
    :param profile: The Speedy Match site profile of the user (historical model), or None.
    :return: The site ID and the language code.
    :rtype: tuple
    """
    if ((user.is_active) and (profile is not None)):
        for language_code, language_name in django_settings.LANGUAGES:
            if (language_code in (profile.active_languages or [])):
                return django_settings.SPEEDY_MATCH_SITE_ID, language_code
        for language_code, language_name in django_settings.LANGUAGES:
            if (getattr(profile, to_attribute(name='activation_step', language_code=language_code), 0) >= 7):
                return django_settings.SPEEDY_MATCH_SITE_ID, language_code
    return django_settings.SPEEDY_NET_SITE_ID, 'en'


def set_registration_site_id_and_language_code(apps, schema_editor):
    """
    Set registration_site_id and registration_language_code of all users.
    """
    User = apps.get_model('accounts', 'User')
    SiteProfile = apps.get_model('match_accounts', 'SiteProfile')
    profiles = {profile.user_id: profile for profile in SiteProfile.objects.order_by().iterator()}
    for user in User.objects.order_by().iterator():
        site_id, language_code = get_registration_site_id_and_language_code(user=user, profile=profiles.get(user.pk))
        User.objects.filter(pk=user.pk).update(registration_site_id=site_id, registration_language_code=language_code)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_user_registration_site_id_and_more'),
        ('match_accounts', '0019_siteprofile_activation_step_eu_and_more'),
    ]

    operations = [
        migrations.RunPython(set_registration_site_id_and_language_code, migrations.RunPython.noop),
    ]
