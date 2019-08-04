from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group

from friendship.models import Follow, Friend, FriendshipRequest, Block

from speedy.core.admin import admin_site


class ReadOnlyModelAdmin(admin.ModelAdmin):
    """
    ModelAdmin class that prevents modifications through the admin.

    The changelist and the detail view work, but a 403 is returned
    if one actually tries to edit an object.
    """
    actions = None

    # We cannot call super().get_fields(request, obj) because that method calls
    # get_readonly_fields(request, obj), causing infinite recursion. Ditto for
    # super().get_form(request, obj). So we assume the default ModelForm.
    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    # Allow viewing objects but not actually changing them.
    def has_change_permission(self, request, obj=None):
        return (request.method in ['GET', 'HEAD'] and super().has_change_permission(request, obj))

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(Site)
admin_site.register(Site, ReadOnlyModelAdmin)

admin.site.unregister(Group)
# admin_site.register(Group, ReadOnlyModelAdmin)

admin.site.unregister(Block)
admin.site.unregister(Follow)
admin.site.unregister(Friend)
admin.site.unregister(FriendshipRequest)
# admin_site.register(Block, ReadOnlyModelAdmin)
# admin_site.register(Follow, ReadOnlyModelAdmin)
admin_site.register(Friend, ReadOnlyModelAdmin)
admin_site.register(FriendshipRequest, ReadOnlyModelAdmin)


class Friend1(object):
    def __str__(self):
        return "User {} is friends with {}".format(self.to_user, self.from_user)


class FriendshipRequest1(object):
    def __str__(self):
        return "Friendship request from user {} to {}".format(self.from_user, self.to_user)


Friend.__str__ = Friend1.__str__
FriendshipRequest.__str__ = FriendshipRequest1.__str__


