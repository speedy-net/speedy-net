from django.contrib import admin
from django.contrib.auth.models import User
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from base.models import *
from friendship.models import Friend

def get_admin_url(obj):
    """ Helper to get admin change url for the object """
    content_type = ContentType.objects.get_for_model(obj.__class__)
    return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(obj.id,))


class UserProfileAdmin(admin.ModelAdmin):
    pass

class UserMessagesAdmin(admin.ModelAdmin):
    pass


def friendship(obj):
    """ custom friendship admin link """
    title = "%s friends with %s." % (obj.from_user.username, obj.to_user.username)
    return mark_safe('<a href="%s" target="_blank">%s</a>' % (get_admin_url(obj), title))

class FriendAdmin(admin.ModelAdmin):
    """ Custom representation of the Friend model in the admin

        list_display - define fields to be displayed on the list page for the model.
        search_fields - define searchable fields

        Grappelli offers a easy autocomplete integration for the change/add pages of a model.
        by default, Django adds a select dropdown for foreign key fields, this dropdown may contain
        many results and it may take long time to fetch them, autocomplete lookup adds an api endpoint for these fields
        and they are loaded in smaller chunks.

        raw_id_fields - specify foreign key field name
        autocomplete_lookup_fields - add them to the lookups
    """
    list_display = (friendship,)
    search_fields = ('from_user',)

    raw_id_fields = ['from_user', 'to_user']
    autocomplete_lookup_fields = {
        'fk': ['from_user', 'to_user']
    }


def friendship_request(obj):
    """ custom friendship request admin link """
    title = "%s friends with %s." % (obj.from_user.username, obj.to_user.username)
    return mark_safe('<a href="%s" target="_blank">%s</a>' % (get_admin_url(obj), title))

class FriendshipRequestAdmin(admin.ModelAdmin):
    """ Custom representation of the FriendshipRequest model in the admin """
    raw_id_fields = ['from_user', 'to_user']
    autocomplete_lookup_fields = {
        'fk': ['from_user', 'to_user']
    }
    list_display = (friendship_request,)

# unregister friendship app models that we have overwritten
admin.site.unregister(Friend)
admin.site.unregister(FriendshipRequest)

# Register your models here.
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserMessage, UserMessagesAdmin)
admin.site.register(Friend, FriendAdmin)
admin.site.register(FriendshipRequest, FriendshipRequestAdmin)
