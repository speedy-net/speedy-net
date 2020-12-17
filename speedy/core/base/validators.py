from django.conf import settings as django_settings
from django.core.validators import FileExtensionValidator, RegexValidator
from django.utils.translation import gettext_lazy as _


regular_udid_validator = RegexValidator(regex=r'^[1-9][0-9]{19}$', message=_("id contains illegal characters."))
small_udid_validator = RegexValidator(regex=r'^[1-9][0-9]{14}$', message=_("id contains illegal characters."))


def validate_image_file_extension(value):
    return FileExtensionValidator(allowed_extensions=django_settings.IMAGE_FILE_EXTENSIONS)(value)
