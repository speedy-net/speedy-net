from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig

from speedy.core.patches import auth_patches
from speedy.core.patches import friendship_patches
from speedy.core.patches import locale_patches
from speedy.core.patches import session_patches


class SpeedyCoreBaseAppConfig(AppConfig):
    """
    App config for the Speedy Core Base app.

    Attributes:
        default (bool): Whether this is the default app config for the app.
        name (str): The full Python path to the application.
        verbose_name (str): The human-readable name of the app.
        label (str): The short name of the app.

    Methods:
        ready: Applies the Speedy Core patches when the app is ready.
    """
    default = True
    name = 'speedy.core.base'
    verbose_name = _("Speedy Core Base App")
    label = 'base'

    def ready(self):
        """
        Applies the auth, friendship, locale and session patches once the app registry is fully populated.
        """
        auth_patches.patch()
        friendship_patches.patch()
        locale_patches.patch()
        session_patches.patch()


