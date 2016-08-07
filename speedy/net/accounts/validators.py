from django.core import validators
from django.utils.translation import ugettext_lazy as _

identity_id_validator = validators.RegexValidator(regex=r'[0-9]', message=_('ID contains illegal characters.'))
username_validator = validators.RegexValidator(regex=r'[a-z0-9]', message=_('Username contains illegal characters.'))
