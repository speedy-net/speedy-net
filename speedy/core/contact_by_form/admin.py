"""
Django admin configuration for the contact by form app of Speedy Core, which registers a read-only admin for the Feedback model.
"""
from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Feedback


class FeedbackAdmin(ReadOnlyModelAdmin):
    """
    Read-only admin interface for Feedback entries.

    Attributes:
        readonly_fields (tuple): Fields shown as read-only in the admin (creation/update timestamps and id).
    """
    readonly_fields = ('date_created', 'date_updated', 'id')


admin.site.register(Feedback, FeedbackAdmin)


