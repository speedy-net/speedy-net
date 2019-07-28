from django.conf import settings as django_settings
from django.contrib import admin

from translated_fields import TranslatedFieldAdmin

from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Entity, ReservedUsername, User, UserEmailAddress


class ReservedUsernameAdmin(admin.ModelAdmin):
    readonly_fields = ('date_created', 'date_updated', 'id')


class UserAdmin(TranslatedFieldAdmin, ReadOnlyModelAdmin):
    pass


class UserEmailAddressAdmin(ReadOnlyModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return True


class SiteProfileBaseAdmin(TranslatedFieldAdmin, ReadOnlyModelAdmin):
    pass


admin.site.register(Entity, ReadOnlyModelAdmin)
admin.site.register(ReservedUsername, ReservedUsernameAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UserEmailAddress, UserEmailAddressAdmin)


if (django_settings.DEBUG):
    admin.site.unregister(UserEmailAddress)
    admin.site.register(UserEmailAddress)


