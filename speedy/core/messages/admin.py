from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin, ReadOnlyModelAdmin2000, ReadOnlyTabularInlinePaginatedModelAdmin
from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
from .models import Chat, Message


class MessageInlineAdmin(ReadOnlyTabularInlinePaginatedModelAdmin):
    model = Message
    per_page = 100
    readonly_fields = ('date_created', 'date_updated', 'id')

    def get_queryset(self, request):
        return super().get_queryset(request=request).prefetch_related(
            'chat__ent1__user__{}'.format(SpeedyMatchSiteProfile.RELATED_NAME),
            'chat__ent1__user__{}'.format(SpeedyNetSiteProfile.RELATED_NAME),
            'chat__ent2__user__{}'.format(SpeedyMatchSiteProfile.RELATED_NAME),
            'chat__ent2__user__{}'.format(SpeedyNetSiteProfile.RELATED_NAME),
            'chat__messages__sender',
            'sender',
        )


class ChatAdmin(ReadOnlyModelAdmin):
    readonly_fields = ('date_created', 'date_updated', 'id')
    inlines = [
        MessageInlineAdmin,
    ]


class MessageAdmin(ReadOnlyModelAdmin2000):
    readonly_fields = ('date_created', 'date_updated', 'id')


admin.site.register(Chat, ChatAdmin)
admin.site.register(Message, MessageAdmin)


