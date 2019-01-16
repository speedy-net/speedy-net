from django.contrib import admin
from .models import User, Entity, UserEmailAddress


class EntityAdmin(admin.ModelAdmin):
    fields = ('date_created', 'date_updated', 'id', 'username', 'slug', 'photo')
    readonly_fields = ('date_created', 'date_updated', 'id', 'username', 'slug', 'photo')


class UserAdmin(admin.ModelAdmin):
    # fields = ('date_created', 'date_updated')
    readonly_fields = ('date_created', 'date_updated', 'id', 'first_name', 'last_name')


class UserEmailAddressAdmin(admin.ModelAdmin):
    pass


admin.site.register(Entity, EntityAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UserEmailAddress, UserEmailAddressAdmin)


