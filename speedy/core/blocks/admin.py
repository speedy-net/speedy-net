"""
Django admin configuration for the blocks app of Speedy Core, which registers a read-only admin for the Block model.
"""
from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Block


class BlockAdmin(ReadOnlyModelAdmin):
    """
    Read-only admin interface for the Block model.
    """
    readonly_fields = ('date_created', 'date_updated', 'id')


admin.site.register(Block, BlockAdmin)


