from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import string
        import random

        from speedy.core.accounts.models import User


        def get_random_user_password_length():
            return random.randint(User.settings.MIN_PASSWORD_LENGTH, User.settings.MAX_PASSWORD_LENGTH)


        def get_random_user_password():
            user_password_length = get_random_user_password_length()
            user_password = ''.join(random.choice(string.digits + string.ascii_letters + string.punctuation + ' ') for _i in range(user_password_length))
            if (len(set(list(user_password))) < User.settings.MIN_PASSWORD_UNIQUE_CHARACTERS):
                user_password = string.ascii_lowercase[:User.settings.MIN_PASSWORD_UNIQUE_CHARACTERS] + user_password[User.settings.MIN_PASSWORD_UNIQUE_CHARACTERS:]
            if (len(user_password) == user_password_length):
                return user_password
            else:
                raise Exception("Unexpected: len(user_password)={}, user_password_length={}".format(len(user_password), user_password_length))


    def get_django_settings_class_with_override_settings(django_settings_class, **override_settings):
        class django_settings_class_with_override_settings(django_settings_class):
            pass

        for setting, value in override_settings.items():
            setattr(django_settings_class_with_override_settings, setting, value)

        return django_settings_class_with_override_settings


