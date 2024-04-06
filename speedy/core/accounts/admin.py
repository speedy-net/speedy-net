from django.conf import settings as django_settings

from translated_fields import TranslatedFieldAdmin

from speedy.core.base.admin import ModelAdmin, ModelAdmin15000, ReadOnlyModelAdmin2500


class SiteProfileBaseAdmin(TranslatedFieldAdmin, ReadOnlyModelAdmin2500):
    readonly_fields = ('date_created', 'date_updated')

    def has_delete_permission(self, request, obj=None):
        return True


if (django_settings.LOGIN_ENABLED):
    from speedy.core import admin
    from speedy.core.messages.admin import MessageInlineAdmin
    from speedy.core.accounts.utils import get_site_profile_model
    from .models import Entity, ReservedUsername, User, UserEmailAddress

    SiteProfile = get_site_profile_model()


    class EntityAdmin(TranslatedFieldAdmin, ReadOnlyModelAdmin2500):
        readonly_fields = ('date_created', 'date_updated', 'id')
        inlines = [
            MessageInlineAdmin,
        ]

        def has_delete_permission(self, request, obj=None):
            return True


    class ReservedUsernameAdmin(ModelAdmin15000):
        readonly_fields = ('date_created', 'date_updated', 'id')


    class UserAdmin(TranslatedFieldAdmin, ReadOnlyModelAdmin2500):
        readonly_fields = ('date_created', 'date_updated', 'id')
        inlines = [
            MessageInlineAdmin,
        ]
        ordering = ('-{}__last_visit'.format(SiteProfile.RELATED_NAME),)

        def has_delete_permission(self, request, obj=None):
            return True


    class UserEmailAddressAdmin(ReadOnlyModelAdmin2500):
        readonly_fields = ('date_created', 'date_updated', 'id')

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


