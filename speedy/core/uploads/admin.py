from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin5000
from .models import File, Image


class FileOwnerAdminMixin(object):
    def get_queryset(self, request):
        return super().get_queryset(request=request).prefetch_related(
            'owner',
        )


class FileAdmin(FileOwnerAdminMixin, ReadOnlyModelAdmin5000):
    pass


class ImageAdmin(FileOwnerAdminMixin, ReadOnlyModelAdmin5000):
    pass


admin.site.register(File, FileAdmin)
admin.site.register(Image, ImageAdmin)


