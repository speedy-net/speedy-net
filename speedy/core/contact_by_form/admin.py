from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Feedback


class FeedbackAdmin(ReadOnlyModelAdmin):
    readonly_fields = ('date_created', 'date_updated', 'id')


admin.site.register(Feedback, FeedbackAdmin)


