from django.views import generic
from rules.contrib.views import PermissionRequiredMixin

from speedy.net.profiles.views import UserMixin

from .models import Chat


class ChatListView(UserMixin, PermissionRequiredMixin, generic.ListView):

    permission_required = 'im.view_chats'

    def get_queryset(self):
        return Chat.on_site.chats(self.user).select_related('ent1', 'ent2')
