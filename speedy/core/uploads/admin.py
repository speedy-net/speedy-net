from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin15000
from .models import File, Image


class FileOwnerAdminMixin(object):
    def get_queryset(self, request):
        return super().get_queryset(request=request).prefetch_related(
            'owner',
        )


class FileAdmin(FileOwnerAdminMixin, ReadOnlyModelAdmin15000):
    readonly_fields = ('date_created', 'date_updated', 'id')


class ImageAdmin(FileOwnerAdminMixin, ReadOnlyModelAdmin15000):
    readonly_fields = ('date_created', 'date_updated', 'id')


admin.site.register(File, FileAdmin)
admin.site.register(Image, ImageAdmin)


