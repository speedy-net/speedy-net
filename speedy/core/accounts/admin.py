from django.contrib import admin

from translated_fields import TranslatedFieldAdmin

from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Entity, ReservedUsername, User, UserEmailAddress


class ReservedUsernameAdmin(admin.ModelAdmin):
    readonly_fields = ('date_created', 'date_updated', 'id')


class UserAdmin(TranslatedFieldAdmin, admin.ModelAdmin):
    readonly_fields = ('date_created', 'date_updated', 'id', 'is_superuser', 'is_staff')


class UserEmailAddressAdmin(ReadOnlyModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return True


class SiteProfileBaseAdmin(TranslatedFieldAdmin, admin.ModelAdmin):
    readonly_fields = ('date_created', 'date_updated', 'user', 'last_visit')


admin.site.register(Entity, ReadOnlyModelAdmin)
admin.site.register(ReservedUsername, ReservedUsernameAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UserEmailAddress, UserEmailAddressAdmin)


