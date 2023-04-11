from django.contrib import admin as django_admin
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group

from django_admin_inline_paginator.admin import TabularInlinePaginated
from friendship.models import Follow, Friend, FriendshipRequest, Block

from speedy.core import admin


class ModelAdmin(django_admin.ModelAdmin):
    list_per_page = 250


class ModelAdmin5000(ModelAdmin):
    list_per_page = 5000


class ModelAdmin15000(ModelAdmin):
    list_per_page = 15000


class ReadOnlyModelAdminMixin(object):
    """
    ModelAdmin class that prevents modifications through the admin.

    The changelist and the detail view work, but a 403 is returned
    if one actually tries to edit an object.
    """
    actions = None

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReadOnlyModelAdmin(ReadOnlyModelAdminMixin, ModelAdmin):
    pass


class ReadOnlyModelAdmin2000(ReadOnlyModelAdmin):
    list_per_page = 2000


class ReadOnlyModelAdmin5000(ReadOnlyModelAdmin):
    list_per_page = 5000


class ReadOnlyModelAdmin15000(ReadOnlyModelAdmin):
    list_per_page = 15000


class ReadOnlyTabularInlineModelAdmin(ReadOnlyModelAdminMixin, django_admin.TabularInline):
    pass


class ReadOnlyTabularInlinePaginatedModelAdmin(ReadOnlyModelAdminMixin, TabularInlinePaginated):
    pass


class ReadOnlyStackedInlineModelAdmin(ReadOnlyModelAdminMixin, django_admin.StackedInline):
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
    def __str__(self):
        return "User {} is friends with {}".format(self.to_user, self.from_user)


class _FriendshipRequest(object):
    def __str__(self):
        return "Friendship request from user {} to {}".format(self.from_user, self.to_user)


Friend.__str__ = _Friend.__str__
FriendshipRequest.__str__ = _FriendshipRequest.__str__


