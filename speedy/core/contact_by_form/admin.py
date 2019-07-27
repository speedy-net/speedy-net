from django.conf import settings as django_settings
from django.contrib import admin

from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Feedback


admin.site.register(Feedback, ReadOnlyModelAdmin)


