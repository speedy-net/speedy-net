from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from rules.contrib.views import PermissionRequiredMixin

from speedy.net.profiles.views import UserMixin
from .models import Block


class BlockListView(UserMixin, PermissionRequiredMixin, generic.ListView):
    permission_required = 'accounts.edit_profile'

    def get_queryset(self):
        return Block.objects.filter(blocker=self.user)


class BlockView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'blocks.block'

    def get(self, request, *args, **kwargs):
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        Block.objects.block(request.user, self.user)
        messages.success(request, _('You have blocked this user.'))
        return redirect(to=self.user)


class UnblockView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'blocks.unblock'

    def get(self, request, *args, **kwargs):
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        Block.objects.unblock(request.user, self.user)
        messages.success(request, _('You have unblocked this user.'))
        return redirect(to=self.user)
