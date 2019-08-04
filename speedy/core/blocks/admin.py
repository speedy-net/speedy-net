from speedy.core.admin import admin_site
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Block


admin_site.register(Block, ReadOnlyModelAdmin)


