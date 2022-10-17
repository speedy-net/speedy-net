from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin, ReadOnlyModelAdmin2000, ReadOnlyTabularInlinePaginatedModelAdmin
from .models import Chat, Message


class MessageInlineAdmin(ReadOnlyTabularInlinePaginatedModelAdmin):
    model = Message
    per_page = 100

    def get_queryset(self, request):
        return super().get_queryset(request=request).prefetch_related(
            'chat__ent1__user__speedy_match_site_profile',
            'chat__ent1__user__speedy_net_site_profile',
            'chat__ent2__user__speedy_match_site_profile',
            'chat__ent2__user__speedy_net_site_profile',
            'chat__messages__sender',
            'sender',
        )


admin.site.register(Chat, ReadOnlyModelAdmin)
admin.site.register(Message, ReadOnlyModelAdmin2000)


