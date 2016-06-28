from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from friendship.models import Friend
from rules.contrib.views import PermissionRequiredMixin

from speedy.net.profiles.views import UserMixin


class UserFriendListView(UserMixin, generic.TemplateView):
    template_name = 'friends/friend_list.html'

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'friend_list': Friend.objects.friends(self.user),
            'request_list': Friend.objects.requests(self.user),
        })
        return cd


class FriendRequestView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'friends.request'

    def get(self, request, *args, **kwargs):
        return self.user.get_absolute_url()

    def post(self, request, *args, **kwargs):
        Friend.objects.add_friend(request.user, self.user)
        messages.success(request, _('Friend request sent.'))
        return redirect(self.user.get_absolute_url())


class AcceptRejectFriendRequestViewBase(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'friends.view_requests'

    def get(self, request, *args, **kwargs):
        return self.user.get_absolute_url()

    def post(self, request, *args, **kwargs):
        frequest = get_object_or_404(
            self.user.friendship_requests_received,
            id=kwargs.get('friendship_request_id'))
        getattr(frequest, self.action)()
        messages.success(request, self.message)
        return redirect('friends:list', username=request.user.slug)


class AcceptFriendRequestView(AcceptRejectFriendRequestViewBase):
    action = 'accept'
    message = _('Friend request accepted.')


class RejectFriendRequestView(AcceptRejectFriendRequestViewBase):
    action = 'reject'
    message = _('Friend request rejected.')
