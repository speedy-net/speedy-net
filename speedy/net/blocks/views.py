from django.views import generic
from rules.contrib.views import PermissionRequiredMixin

from speedy.core.profiles.views import UserMixin
from speedy.core.blocks.models import Block


class BlockedUsersListView(UserMixin, PermissionRequiredMixin, generic.ListView):
    """
    Displays the paginated list of users blocked by the current user on Speedy Net.

    Attributes:
        permission_required (str): The permission required to view the blocked users list.
        page_size (int): The number of blocked users displayed per page.
        paginate_by (int): The number of items per page, used by Django's ListView pagination.

    Methods:
        get_queryset(self): Returns the queryset of users blocked by the current user.
    """
    permission_required = 'accounts.view_blocked_users_list'
    page_size = 24
    paginate_by = page_size

    def get_queryset(self):
        """
        Returns the queryset of users blocked by the current user.

        :return: A queryset of blocked users.
        :rtype: django.db.models.QuerySet
        """
        return Block.objects.get_blocked_list_to_queryset(blocker=self.user)


