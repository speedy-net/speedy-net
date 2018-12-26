from django.conf import settings

from speedy.core.base.utils import conditional_method_or_class


only_if_login_is_enabled = lambda site_id: conditional_method_or_class(conditional_function=lambda: (settings.LOGIN_ENABLED))


