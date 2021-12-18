from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyCoreContactByFormAppConfig(AppConfig):
    default = True
    name = 'speedy.core.contact_by_form'
    verbose_name = _("Contact By Form")


