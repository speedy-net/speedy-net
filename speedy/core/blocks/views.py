from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import generic
from rules.contrib.views import PermissionRequiredMixin

from speedy.core.profiles.views import UserMixin
from .models import Block


class BlockView(UserMixin, PermissionRequiredMixin, generic.View):
    """
    View allowing a logged-in user to block another user.

    Attributes:
        permission_required (str): The permission required to block a user ('blocks.block').

    Methods:
        get(self, request, *args, **kwargs): Redirect to the user's profile page without blocking.
        post(self, request, *args, **kwargs): Block the user and redirect to the user's profile page.
    """
    permission_required = 'blocks.block'

    def get(self, request, *args, **kwargs):
        """
        Redirect to the user's profile page without performing any block action.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the user's profile page.
        :rtype: django.http.HttpResponseRedirect
        """
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        """
        Block the user and redirect to the user's profile page.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the user's profile page.
        :rtype: django.http.HttpResponseRedirect
        """
        Block.objects.block(blocker=request.user, blocked=self.user)
        messages.success(request=request, message=_('You have blocked {}.').format(self.user.name))
        return redirect(to=self.user)


class UnblockView(UserMixin, PermissionRequiredMixin, generic.View):
    """
    View allowing a logged-in user to unblock a previously blocked user.

    Attributes:
        permission_required (str): The permission required to unblock a user ('blocks.unblock').

    Methods:
        get(self, request, *args, **kwargs): Redirect to the user's profile page without unblocking.
        post(self, request, *args, **kwargs): Unblock the user and redirect to the user's profile page.
    """
    permission_required = 'blocks.unblock'

    def get(self, request, *args, **kwargs):
        """
        Redirect to the user's profile page without performing any unblock action.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the user's profile page.
        :rtype: django.http.HttpResponseRedirect
        """
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        """
        Unblock the user and redirect to the user's profile page.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the user's profile page.
        :rtype: django.http.HttpResponseRedirect
        """
        Block.objects.unblock(blocker=request.user, blocked=self.user)
        messages.success(request=request, message=_('You have unblocked {}.').format(self.user.name))
        return redirect(to=self.user)


