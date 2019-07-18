from django.contrib import admin

from translated_fields import TranslatedFieldAdmin

from .models import Entity, ReservedUsername, User, UserEmailAddress


class EntityAdmin(admin.ModelAdmin):
    # fields = ('date_created', 'date_updated', 'id', 'username', 'slug', 'photo')
    readonly_fields = ('date_created', 'date_updated', 'id', 'username', 'slug', 'photo')


class ReservedUsernameAdmin(admin.ModelAdmin):
    readonly_fields = ('date_created', 'date_updated', 'id')


class UserAdmin(TranslatedFieldAdmin, admin.ModelAdmin):
    # fields = ('date_created', 'date_updated')
    readonly_fields = ('date_created', 'date_updated', 'id')


class UserEmailAddressAdmin(admin.ModelAdmin):
    pass


class SiteProfileBaseAdmin(TranslatedFieldAdmin, admin.ModelAdmin):
    readonly_fields = ('date_created', 'date_updated', 'user', 'last_visit')


admin.site.register(Entity, EntityAdmin)
admin.site.register(ReservedUsername, ReservedUsernameAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UserEmailAddress, UserEmailAddressAdmin)


