from django.contrib import admin as django_admin
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group

from django_admin_inline_paginator_plus.admin import TabularInlinePaginated
from friendship.models import Follow, Friend, FriendshipRequest, Block

from speedy.core import admin


class ModelAdmin(django_admin.ModelAdmin):
    """
    The base ModelAdmin class for Speedy Core, showing 250 items per page.
    """
    list_per_page = 250


class ModelAdmin5000(ModelAdmin):
    """
    A ModelAdmin class showing 5000 items per page.
    """
    list_per_page = 5000


class ModelAdmin15000(ModelAdmin):
    """
    A ModelAdmin class showing 15000 items per page.
    """
    list_per_page = 15000


class ReadOnlyModelAdminMixin(object):
    """
    ModelAdmin class that prevents modifications through the admin.

    The changelist and the detail view work, but a 403 is returned
    if one actually tries to edit an object.
    """
    actions = None

    def has_add_permission(self, request, obj=None):
        """
        Prevents adding objects through the admin.

        :param request: The current request.
        :param obj: The object being added, if any. Default None.
        :return: False, always.
        :rtype: bool
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Prevents changing objects through the admin.

        :param request: The current request.
        :param obj: The object being changed, if any. Default None.
        :return: False, always.
        :rtype: bool
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Prevents deleting objects through the admin.

        :param request: The current request.
        :param obj: The object being deleted, if any. Default None.
        :return: False, always.
        :rtype: bool
        """
        return False


class ReadOnlyModelAdmin(ReadOnlyModelAdminMixin, ModelAdmin):
    """
    A read-only ModelAdmin class, showing 250 items per page.
    """
    pass


class ReadOnlyModelAdmin2000(ReadOnlyModelAdmin):
    """
    A read-only ModelAdmin class, showing 2000 items per page.
    """
    list_per_page = 2000


class ReadOnlyModelAdmin2500(ReadOnlyModelAdmin):
    """
    A read-only ModelAdmin class, showing 2500 items per page.
    """
    list_per_page = 2500


class ReadOnlyModelAdmin5000(ReadOnlyModelAdmin):
    """
    A read-only ModelAdmin class, showing 5000 items per page.
    """
    list_per_page = 5000


class ReadOnlyModelAdmin15000(ReadOnlyModelAdmin):
    """
    A read-only ModelAdmin class, showing 15000 items per page.
    """
    list_per_page = 15000


class ReadOnlyTabularInlineModelAdmin(ReadOnlyModelAdminMixin, django_admin.TabularInline):
    """
    A read-only tabular inline ModelAdmin class.
    """
    pass


class ReadOnlyTabularInlinePaginatedModelAdmin(ReadOnlyModelAdminMixin, TabularInlinePaginated):
    """
    A read-only paginated tabular inline ModelAdmin class.
    """
    pass


class ReadOnlyStackedInlineModelAdmin(ReadOnlyModelAdminMixin, django_admin.StackedInline):
    """
    A read-only stacked inline ModelAdmin class.
    """
    pass


django_admin.site.unregister(Site)
admin.site.register(Site, ReadOnlyModelAdmin)

django_admin.site.unregister(Group)
# admin.site.register(Group, ReadOnlyModelAdmin)

django_admin.site.unregister(Block)
django_admin.site.unregister(Follow)
django_admin.site.unregister(Friend)
django_admin.site.unregister(FriendshipRequest)
# admin.site.register(Block, ReadOnlyModelAdmin)
# admin.site.register(Follow, ReadOnlyModelAdmin)
admin.site.register(Friend, ReadOnlyModelAdmin)
admin.site.register(FriendshipRequest, ReadOnlyModelAdmin)


class _Friend(object):
    """
    A helper class used only to provide a `__str__` method to monkey-patch onto `friendship.models.Friend`.
    """
    def __str__(self):
        """
        Returns a human-readable string representation of the friendship.

        :return: A string describing which user is friends with which other user.
        :rtype: str
        """
        return "User {} is friends with {}".format(self.to_user, self.from_user)


class _FriendshipRequest(object):
    """
    A helper class used only to provide a `__str__` method to monkey-patch onto `friendship.models.FriendshipRequest`.
    """
    def __str__(self):
        """
        Returns a human-readable string representation of the friendship request.

        :return: A string describing the friendship request from one user to another.
        :rtype: str
        """
        return "Friendship request from user {} to {}".format(self.from_user, self.to_user)


Friend.__str__ = _Friend.__str__
FriendshipRequest.__str__ = _FriendshipRequest.__str__


