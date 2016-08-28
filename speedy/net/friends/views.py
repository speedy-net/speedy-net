from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from friendship.models import Friend
from rules.contrib.views import PermissionRequiredMixin

from speedy.net.profiles.views import UserMixin


class UserFriendListView(UserMixin, generic.TemplateView):
    template_name = 'friends/friend_list.html'


class FriendRequestView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'friends.request'

    def get(self, request, *args, **kwargs):
        return redirect(self.user)

    def post(self, request, *args, **kwargs):
        # Check if the requesting user has less than MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED friends?
        # ~~~~ TODO: this code appears twice, combine to one place.
        user_number_of_friends = len(Friend.objects.friends(request.user))
        if (user_number_of_friends >= settings.MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED):
            messages.error(request, _("You already have {0} friends. You can't have more than {0} friends on Speedy Net. Please remove friends before you proceed.".format(settings.MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED)))
            return redirect(self.user)
        Friend.objects.add_friend(request.user, self.user)
        messages.success(request, _('Friend request sent.'))
        return redirect(self.user)


class AcceptRejectFriendRequestViewBase(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'friends.view_requests'

    def get(self, request, *args, **kwargs):
        return self.user.get_absolute_url()

    def post(self, request, *args, **kwargs):
        if (self.action == "accept"):
            # Check if both users have less than MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED friends?
            # ~~~~ TODO: this code appears twice, combine to one place.
            user_number_of_friends = len(Friend.objects.friends(request.user))
            if (user_number_of_friends >= settings.MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED):
                messages.error(request, _("You already have {0} friends. You can't have more than {0} friends on Speedy Net. Please remove friends before you proceed.".format(settings.MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED)))
                return redirect('friends:list', username=request.user.slug)
            other_user_number_of_friends = len(Friend.objects.friends(self.user)) # ~~~~ TODO: This doesn't work, fix! other_user_number_of_friends must be equal to the number of friends of the other user.
            if (other_user_number_of_friends >= settings.MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED):
                messages.error(request, _("This user already has {0} friends. They can't have more than {0} friends on Speedy Net. Please ask them to remove friends before you proceed.".format(settings.MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED)))
                return redirect('friends:list', username=request.user.slug)

        frequest = get_object_or_404(
            self.user.friendship_requests_received,
            id=kwargs.get('friendship_request_id'),
        )
        getattr(frequest, self.action)()
        messages.success(request, self.message)
        return redirect('friends:list', username=request.user.slug)


class AcceptFriendRequestView(AcceptRejectFriendRequestViewBase):
    action = 'accept'
    message = _('Friend request accepted.')


class RejectFriendRequestView(AcceptRejectFriendRequestViewBase):
    action = 'reject'
    message = _('Friend request rejected.')


class RemoveFriendView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'friends.remove'

    def get(self, request, *args, **kwargs):
        return redirect(self.user)

    def post(self, request, *args, **kwargs):
        Friend.objects.remove_friend(self.request.user, self.user)
        messages.success(request, _('You have removed this user from friends.'))
        return redirect(self.user)
