from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


regular_udid_validator = RegexValidator(regex=r'^[1-9][0-9]{19}$', message=_("id contains illegal characters."))
small_udid_validator = RegexValidator(regex=r'^[1-9][0-9]{14}$', message=_("id contains illegal characters."))


