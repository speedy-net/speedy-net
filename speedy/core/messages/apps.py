from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyCoreMessagesAppConfig(AppConfig):
    """
    Django application configuration for the speedy.core.messages app.
    """
    default = True
    name = 'speedy.core.messages'
    verbose_name = _("Messages")
    label = 'core_messages'


