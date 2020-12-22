from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import File, Image


admin.site.register(File, ReadOnlyModelAdmin)
admin.site.register(Image, ReadOnlyModelAdmin)


