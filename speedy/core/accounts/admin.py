from django.conf import settings as django_settings
from django.contrib import admin

from translated_fields import TranslatedFieldAdmin

from speedy.core.admin import admin_site
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Entity, ReservedUsername, User, UserEmailAddress


class ReservedUsernameAdmin(admin.ModelAdmin):
    readonly_fields = ('date_created', 'date_updated', 'id')


class UserAdmin(TranslatedFieldAdmin, ReadOnlyModelAdmin):
    pass


class UserEmailAddressAdmin(ReadOnlyModelAdmin):
    readonly_fields = ('date_created', 'date_updated', 'id')

    def has_delete_permission(self, request, obj=None):
        return True


class SiteProfileBaseAdmin(TranslatedFieldAdmin, ReadOnlyModelAdmin):
    pass


admin_site.register(Entity, ReadOnlyModelAdmin)
admin_site.register(ReservedUsername, ReservedUsernameAdmin)
admin_site.register(User, UserAdmin)

if (django_settings.DEBUG):
    class UserEmailAddressDebugAdmin(admin.ModelAdmin):
        readonly_fields = ('date_created', 'date_updated', 'id')


    admin_site.register(UserEmailAddress, UserEmailAddressDebugAdmin)
else:
    admin_site.register(UserEmailAddress, UserEmailAddressAdmin)


