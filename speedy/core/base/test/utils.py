# from django.conf import settings as django_settings


# def get_user_settings_with_override_settings(override_max_number_of_friends_allowed=None, override_user_settings_min_slug_length=None):
#     class USER_SETTINGS(django_settings.USER_SETTINGS):
#         pass
#     # USER_SETTINGS = django_settings.USER_SETTINGS
#
#     # if (not (override_max_number_of_friends_allowed is None)):
#     #     USER_SETTINGS.MAX_NUMBER_OF_FRIENDS_ALLOWED = override_max_number_of_friends_allowed
#     if (not (override_user_settings_min_slug_length is None)):
#         USER_SETTINGS.MIN_SLUG_LENGTH = override_user_settings_min_slug_length
#
#     return USER_SETTINGS


def get_django_settings_class_with_override_settings(django_settings_class, **override_settings):
    class django_settings_class_with_override_settings(django_settings_class):
        pass

    for setting, value in override_settings.items():
        setattr(django_settings_class_with_override_settings, setting, value)

    return django_settings_class_with_override_settings


