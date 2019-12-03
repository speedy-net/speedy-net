from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyCoreBaseConfig(AppConfig):
    name = 'speedy.core.base'
    verbose_name = _("Speedy Core Base App")
    label = 'base'


