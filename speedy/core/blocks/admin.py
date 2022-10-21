from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Block


class BlockAdmin(ReadOnlyModelAdmin):
    readonly_fields = ('date_created', 'date_updated', 'id')


admin.site.register(Block, BlockAdmin)


