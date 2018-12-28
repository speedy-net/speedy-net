def get_django_settings_class_with_override_settings(django_settings_class, **override_settings):
    class django_settings_class_with_override_settings(django_settings_class):
        pass

    for setting, value in override_settings.items():
        setattr(django_settings_class_with_override_settings, setting, value)

    return django_settings_class_with_override_settings


