from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin5000
from .models import File, Image


admin.site.register(File, ReadOnlyModelAdmin5000)
admin.site.register(Image, ReadOnlyModelAdmin5000)


