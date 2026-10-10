"""
Admin configuration for the Speedy Core uploads app (read-only admin classes for files and images).
"""
from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin15000
from .models import File, Image


class FileOwnerAdminMixin(object):
    """
    Mixin for File/Image admin classes that prefetches the owner relation for the admin changelist queryset.
    """
    def get_queryset(self, request):
        """
        Get the queryset for the admin changelist, with the owner relation prefetched.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :return: The queryset with the owner relation prefetched.
        :rtype: django.db.models.QuerySet
        """
        return super().get_queryset(request=request).prefetch_related(
            'owner',
        )


class FileAdmin(FileOwnerAdminMixin, ReadOnlyModelAdmin15000):
    """
    Read-only admin for the File model.

    Attributes:
        readonly_fields (tuple): The fields displayed as read-only in the admin.
    """
    readonly_fields = ('date_created', 'date_updated', 'id')


class ImageAdmin(FileOwnerAdminMixin, ReadOnlyModelAdmin15000):
    """
    Read-only admin for the Image model.

    Attributes:
        readonly_fields (tuple): The fields displayed as read-only in the admin.
    """
    readonly_fields = ('date_created', 'date_updated', 'id')


admin.site.register(File, FileAdmin)
admin.site.register(Image, ImageAdmin)


