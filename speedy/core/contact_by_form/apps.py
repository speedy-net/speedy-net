from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyCoreContactByFormAppConfig(AppConfig):
    """
    Django app configuration for the contact_by_form app.

    Attributes:
        default (bool): Marks this as the default app config.
        name (str): The dotted Python path of the app.
        verbose_name (str): The human-readable name of the app.
    """
    default = True
    name = 'speedy.core.contact_by_form'
    verbose_name = _("Contact By Form")


