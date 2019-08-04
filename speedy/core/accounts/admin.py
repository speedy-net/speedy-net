from django.conf import settings as django_settings
from django.contrib import admin as django_admin

from translated_fields import TranslatedFieldAdmin

from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Entity, ReservedUsername, User, UserEmailAddress


class ReservedUsernameAdmin(django_admin.ModelAdmin):
    readonly_fields = ('date_created', 'date_updated', 'id')


class UserAdmin(TranslatedFieldAdmin, ReadOnlyModelAdmin):
    pass


class UserEmailAddressAdmin(ReadOnlyModelAdmin):
    readonly_fields = ('date_created', 'date_updated', 'id')

    def has_delete_permission(self, request, obj=None):
        return True


class SiteProfileBaseAdmin(TranslatedFieldAdmin, ReadOnlyModelAdmin):
    pass


admin.site.register(Entity, ReadOnlyModelAdmin)
admin.site.register(ReservedUsername, ReservedUsernameAdmin)
admin.site.register(User, UserAdmin)

if (django_settings.DEBUG):
    class UserEmailAddressDebugAdmin(django_admin.ModelAdmin):
        readonly_fields = ('date_created', 'date_updated', 'id')


    admin.site.register(UserEmailAddress, UserEmailAddressDebugAdmin)
else:
    admin.site.register(UserEmailAddress, UserEmailAddressAdmin)


