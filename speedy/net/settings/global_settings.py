# Used also by Speedy Match.


# ~~~~ TODO: move to speedy.core?


# class EntitySettings(object):
class ENTITY_SETTINGS(object):
    MIN_USERNAME_LENGTH = 6
    MAX_USERNAME_LENGTH = 120

    MIN_SLUG_LENGTH = 6
    MAX_SLUG_LENGTH = 200

    UNAVAILABLE_USERNAMES = [
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


# class NamedEntitySettings(object):
class NAMED_ENTITY_SETTINGS(object):
    MIN_NAME_LENGTH = 1 # ~~~~ TODO: too short?
    MAX_NAME_LENGTH = 200


# class UserSettings(object):
class USER_SETTINGS(object):
    MIN_USERNAME_LENGTH = 6
    MAX_USERNAME_LENGTH = 40

    MIN_SLUG_LENGTH = 6
    MAX_SLUG_LENGTH = 200

    # Users can register from age 0 to 180, but can't be kept on the site after age 250.
    MIN_AGE_ALLOWED_IN_MODEL = 0  # In years.
    MAX_AGE_ALLOWED_IN_MODEL = 250  # In years.

    MIN_AGE_ALLOWED_IN_FORMS = 0  # In years.
    MAX_AGE_ALLOWED_IN_FORMS = 180  # In years.

    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 120

    MAX_NUMBER_OF_FRIENDS_ALLOWED = 800
    # MAX_NUMBER_OF_FRIENDS_ALLOWED = 2 # For testing when there are close to MAX_NUMBER_OF_FRIENDS_ALLOWED friends. # ~~~~ TODO: remove this line!

    PASSWORD_VALIDATORS = [
        {
            'NAME': 'speedy.core.accounts.validators.PasswordMinLengthValidator',
        },
        {
            'NAME': 'speedy.core.accounts.validators.PasswordMaxLengthValidator',
        },
    ]


AUTH_PASSWORD_VALIDATORS = USER_SETTINGS.PASSWORD_VALIDATORS


# ~~~~ TODO: move to django_settings.
DATE_FIELD_FORMATS = [
    '%Y-%m-%d',  # '2006-10-25'
]

DEFAULT_DATE_FIELD_FORMAT = '%Y-%m-%d'


# MAX_NUMBER_OF_FRIENDS_ALLOWED = 800 # ~~~~ TODO: move to class USER_SETTINGS? And then check how can it be overridden in tests.
# MAX_NUMBER_OF_FRIENDS_ALLOWED = 2 # For testing when there are close to MAX_NUMBER_OF_FRIENDS_ALLOWED friends. # ~~~~ TODO: remove this line!


# ENTITY_SETTINGS = EntitySettings
# NAMED_ENTITY_SETTINGS = NamedEntitySettings
# USER_SETTINGS = UserSettings


