from django.views import generic
from rules.contrib.views import PermissionRequiredMixin

from speedy.core.profiles.views import UserMixin
from speedy.core.blocks.models import Block


class BlockedUsersListView(UserMixin, PermissionRequiredMixin, generic.ListView):
    permission_required = 'accounts.view_blocked_users_list'
    page_size = 24
    paginate_by = page_size

    def get_queryset(self):
        return Block.objects.get_blocked_list_to_queryset(blocker=self.user)


