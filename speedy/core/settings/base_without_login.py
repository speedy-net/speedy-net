from .base import *


LOGIN_ENABLED = False


INSTALLED_APPS += [
    'speedy.core.accounts', # ~~~~ TODO: remove this line!
    'speedy.core.im', # ~~~~ TODO: remove this line!
    # 'speedy.core.profiles', # ~~~~ TODO: remove this line!
    # 'speedy.core.friends', # ~~~~ TODO: remove this line!
    'speedy.core.blocks', # ~~~~ TODO: remove this line!
    'speedy.core.uploads', # ~~~~ TODO: remove this line!
    'speedy.core.feedback',
]


MIN_PASSWORD_LENGTH = 8 * 100 # ~~~~ TODO: remove this line!
MAX_PASSWORD_LENGTH = 120 * 100 # ~~~~ TODO: remove this line!

AUTH_USER_MODEL = 'accounts.User' # ~~~~ TODO: remove this line!

UNAVAILABLE_USERNAMES = [] # ~~~~ TODO: remove this line!


