from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import generic
from rules.contrib.views import PermissionRequiredMixin

from speedy.core.profiles.views import UserMixin
from .models import Block


class BlockView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'blocks.block'

    def get(self, request, *args, **kwargs):
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        Block.objects.block(blocker=request.user, blocked=self.user)
        messages.success(request=request, message=_('You have blocked {}.').format(self.user.name))
        return redirect(to=self.user)


class UnblockView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'blocks.unblock'

    def get(self, request, *args, **kwargs):
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        Block.objects.unblock(blocker=request.user, blocked=self.user)
        messages.success(request=request, message=_('You have unblocked {}.').format(self.user.name))
        return redirect(to=self.user)


