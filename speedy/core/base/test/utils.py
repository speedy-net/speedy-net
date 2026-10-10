from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import string
        import random

        from speedy.core.accounts.models import User


        def get_random_user_password_length():
            """
            Returns a random valid password length, between the user model's minimum and maximum password length.

            :return: A random password length.
            :rtype: int
            """
            return random.randint(User.settings.MIN_PASSWORD_LENGTH, User.settings.MAX_PASSWORD_LENGTH)


        def get_random_user_password():
            """
            Generates a random valid password of a random valid length, ensuring it has enough unique characters.

            :return: A random valid password.
            :rtype: str
            :raises Exception: If the generated password's length doesn't match the expected length (unexpected internal error).
            """
            user_password_length = get_random_user_password_length()
            user_password = ''.join(random.choice(string.digits + string.ascii_letters + string.punctuation + ' ') for _i in range(user_password_length))
            if (len(set(list(user_password))) < User.settings.MIN_PASSWORD_UNIQUE_CHARACTERS):
                prefix_list = list(string.ascii_lowercase[:User.settings.MIN_PASSWORD_UNIQUE_CHARACTERS])
                random.shuffle(prefix_list)
                user_password = ''.join(prefix_list) + user_password[User.settings.MIN_PASSWORD_UNIQUE_CHARACTERS:]
            if (len(user_password) == user_password_length):
                return user_password
            else:
                raise Exception("Unexpected: len(user_password)={}, user_password_length={}".format(len(user_password), user_password_length))


    def get_django_settings_class_with_override_settings(django_settings_class, **override_settings):
        """
        Builds a subclass of the given settings class with some attributes overridden.

        :param django_settings_class: Required. The settings class to subclass.
        :type django_settings_class: type
        :param override_settings: Required. Attribute names and values to override on the subclass.
        :return: The new subclass, with the overridden attributes.
        :rtype: type
        """
        class django_settings_class_with_override_settings(django_settings_class):
            """
            A subclass of the given settings class, with some attributes overridden.
            """
            pass

        for setting, value in override_settings.items():
            setattr(django_settings_class_with_override_settings, setting, value)

        return django_settings_class_with_override_settings


