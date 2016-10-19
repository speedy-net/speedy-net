from django.core import validators
from django.utils.translation import ugettext_lazy as _

username_validator = validators.RegexValidator(regex=r'[a-z0-9]', message=_('Username contains illegal characters.'))
slug_validator = validators.RegexValidator(regex=r'[a-z0-9\-]', message=_('Slug contains illegal characters.'))

