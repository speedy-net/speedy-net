from speedy.core.admin import admin_site
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Feedback


admin_site.register(Feedback, ReadOnlyModelAdmin)


