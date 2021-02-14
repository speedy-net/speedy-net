from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyCoreMessagesAppConfig(AppConfig):
    name = 'speedy.core.messages'
    verbose_name = _("Messages")
    label = 'core_messages'


