from .base import *

# Sites without login are not logged in and are marked as under construction.
LOGIN_ENABLED = False
THIS_SITE_IS_UNDER_CONSTRUCTION = True

INSTALLED_APPS += [
    'speedy.core.contact_by_email',
]


