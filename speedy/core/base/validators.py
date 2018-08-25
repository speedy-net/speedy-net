from django.core import validators


regular_udid_validator = validators.RegexValidator(regex=r'^[1-9][0-9]{19}$', message="id contains illegal characters")
small_udid_validator = validators.RegexValidator(regex=r'^[1-9][0-9]{14}$', message="id contains illegal characters")


