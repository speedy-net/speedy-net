"""
Global settings of Speedy Net - the entity, named entity and user settings.
"""


# Used also by Speedy Match.


# ~~~~ TODO: move to speedy.core?


class ENTITY_SETTINGS(object):
    """
    Settings for entities (any named/slugged object on the site, such as users).
    """
    # Minimum and maximum length of an entity's username.
    MIN_USERNAME_LENGTH = 6
    MAX_USERNAME_LENGTH = 120

    # Minimum and maximum length of an entity's slug.
    MIN_SLUG_LENGTH = 6
    MAX_SLUG_LENGTH = 200

    # Usernames and slugs which can't be registered, because they are used as URL paths or are reserved names.
    RESERVED_USERNAMES = [
        'about',
        'admin',
        'contact',
        'css',
        'domain',
        'editprofile',
        'feedback',
        'friends',
        'i18n',
        'icons',
        'images',
        'javascript',
        'js',
        'locale',
        'login',
        'logout',
        'mail',
        'me',
        'messages',
        'postmaster',
        'python',
        'register',
        'report',
        'resetpassword',
        'root',
        'setsession',
        'speedy',
        'speedycomposer',
        'speedymail',
        'speedymailsoftware',
        'speedymatch',
        'speedynet',
        'static',
        'uri',
        'webmaster',
        'welcome',
    ]


class NAMED_ENTITY_SETTINGS(object):
    """
    Settings for named entities (entities that have a name, such as users).
    """
    # Minimum and maximum length of a name of a named entity.
    MIN_NAME_LENGTH = 1  # ~~~~ TODO: too short?
    MAX_NAME_LENGTH = 200


class USER_SETTINGS(object):
    """
    Settings for users.
    """
    # Minimum and maximum length of a user's username.
    MIN_USERNAME_LENGTH = 6
    MAX_USERNAME_LENGTH = 40

    # Minimum and maximum length of a user's slug.
    MIN_SLUG_LENGTH = 6
    MAX_SLUG_LENGTH = 200

    # Users can register from age 0 to 180, but can't be kept on the site after age 250.
    MIN_AGE_ALLOWED_IN_MODEL = 0  # In years.
    MAX_AGE_ALLOWED_IN_MODEL = 250  # In years.

    # Minimum and maximum age (in years) accepted in forms (such as the date of birth field).
    MIN_AGE_ALLOWED_IN_FORMS = 0  # In years.
    MAX_AGE_ALLOWED_IN_FORMS = 180  # In years.

    # Minimum and maximum length of a password, and the minimum number of unique characters it must contain.
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 120
    MIN_PASSWORD_UNIQUE_CHARACTERS = 6

    # Maximum number of friends a user can have.
    MAX_NUMBER_OF_FRIENDS_ALLOWED = 800

    # Password validators used by Django's AUTH_PASSWORD_VALIDATORS (minimum length, maximum length and minimum unique characters).
    PASSWORD_VALIDATORS = [
        {
            'NAME': 'speedy.core.accounts.validators.PasswordMinLengthValidator',
        },
        {
            'NAME': 'speedy.core.accounts.validators.PasswordMaxLengthValidator',
        },
        {
            'NAME': 'speedy.core.accounts.validators.PasswordMinUniqueCharsValidator',
        },
    ]


# Django's password validators for all sites, taken from the user settings above.
AUTH_PASSWORD_VALIDATORS = USER_SETTINGS.PASSWORD_VALIDATORS

# ENTITY_SETTINGS = EntitySettings
# NAMED_ENTITY_SETTINGS = NamedEntitySettings
# USER_SETTINGS = UserSettings


