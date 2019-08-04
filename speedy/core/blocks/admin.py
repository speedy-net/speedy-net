from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Block


admin.site.register(Block, ReadOnlyModelAdmin)


