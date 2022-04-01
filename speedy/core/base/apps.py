from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig

from speedy.core.patches import friendship_patches
from speedy.core.patches import locale_patches
from speedy.core.patches import session_patches


class SpeedyCoreBaseAppConfig(AppConfig):
    default = True
    name = 'speedy.core.base'
    verbose_name = _("Speedy Core Base App")
    label = 'base'

    def ready(self):
        friendship_patches.patch()
        locale_patches.patch()
        session_patches.patch()


