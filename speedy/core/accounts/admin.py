from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from translated_fields import TranslatedFieldAdmin

    from speedy.core import admin
    from speedy.core.base.admin import ModelAdmin, ModelAdmin5000, ReadOnlyModelAdmin
    from speedy.core.messages.admin import MessageInlineAdmin
    from speedy.core.accounts.utils import get_site_profile_model
    from .models import Entity, ReservedUsername, User, UserEmailAddress

    SiteProfile = get_site_profile_model()


    class EntityAdmin(TranslatedFieldAdmin, ReadOnlyModelAdmin):
        readonly_fields = ('date_created', 'date_updated', 'id')
        inlines = [
            MessageInlineAdmin,
        ]

        def has_delete_permission(self, request, obj=None):
            return True


    class ReservedUsernameAdmin(ModelAdmin5000):
        readonly_fields = ('date_created', 'date_updated', 'id')


    class UserAdmin(TranslatedFieldAdmin, ReadOnlyModelAdmin):
        readonly_fields = ('date_created', 'date_updated', 'id')
        inlines = [
            MessageInlineAdmin,
        ]
        ordering = ('-{}__last_visit'.format(SiteProfile.RELATED_NAME),)

        def has_delete_permission(self, request, obj=None):
            return True


    class UserEmailAddressAdmin(ReadOnlyModelAdmin):
        readonly_fields = ('date_created', 'date_updated', 'id')

        def has_delete_permission(self, request, obj=None):
            return True


    class SiteProfileBaseAdmin(TranslatedFieldAdmin, ReadOnlyModelAdmin):
        def has_delete_permission(self, request, obj=None):
            return True


    admin.site.register(Entity, EntityAdmin)
    admin.site.register(ReservedUsername, ReservedUsernameAdmin)
    admin.site.register(User, UserAdmin)

    if (django_settings.DEBUG):
        class UserEmailAddressDebugAdmin(ModelAdmin):
            readonly_fields = ('date_created', 'date_updated', 'id')


        admin.site.register(UserEmailAddress, UserEmailAddressDebugAdmin)
    else:
        admin.site.register(UserEmailAddress, UserEmailAddressAdmin)


