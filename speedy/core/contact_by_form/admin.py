from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Feedback


admin.site.register(Feedback, ReadOnlyModelAdmin)


