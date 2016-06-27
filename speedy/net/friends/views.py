from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views import generic
from friendship.exceptions import AlreadyExistsError
from friendship.models import Friend
from rules.contrib.views import LoginRequiredMixin, PermissionRequiredMixin

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


class FriendRequestView(PermissionRequiredMixin, UserMixin, generic.View):
    permission_required = 'friends.request'

    def get(self, request, *args, **kwargs):
        return self.user.get_absolute_url()

    def post(self, request, *args, **kwargs):
        Friend.objects.add_friend(self.request.user, self.user)
        return redirect('friends:list', args=args, kwargs=kwargs)
