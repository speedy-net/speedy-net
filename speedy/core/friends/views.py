from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.views import generic

from friendship.models import Friend, FriendshipRequest
from friendship.exceptions import AlreadyExistsError, AlreadyFriendsError

from rules.contrib.views import PermissionRequiredMixin

from speedy.core.base.views import PaginationMixin
from speedy.core.accounts.models import User
from speedy.core.profiles.views import UserMixin
from .rules import is_self, friendship_request_sent, are_friends


class FriendsMixin(PaginationMixin):
    page_size = 24
    paginate_by = page_size


class UserFriendListView(UserMixin, PermissionRequiredMixin, FriendsMixin, generic.TemplateView):
    # ~~~~ TODO: This view will display up to 800 friends on the same page!
    template_name = 'friends/friend_list.html'
    permission_required = 'friends.view_friend_list'

    def get_object_list(self):
        return self.user.get_friends()

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'friends': self.page.object_list,
        })
        return cd


class ReceivedFriendshipRequestsListView(UserMixin, PermissionRequiredMixin, FriendsMixin, generic.TemplateView):
    template_name = 'friends/received_requests.html'
    permission_required = 'friends.view_requests'

    def get_object_list(self):
        return self.user.get_received_friendship_requests()

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'received_friendship_requests': self.page.object_list,
        })
        return cd


class SentFriendshipRequestsListView(UserMixin, PermissionRequiredMixin, FriendsMixin, generic.TemplateView):
    template_name = 'friends/sent_requests.html'
    permission_required = 'friends.view_requests'

    def get_object_list(self):
        return self.user.get_sent_friendship_requests()

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'sent_friendship_requests': self.page.object_list,
        })
        return cd


class LimitMaxFriendsMixin(object):
    def check_own_friends(self):
        user_number_of_friends = len(Friend.objects.friends(user=self.request.user))
        if (user_number_of_friends >= User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED):
            raise ValidationError(pgettext_lazy(context=self.request.user.get_gender(), message="You already have {0} friends. You can't have more than {1} friends on Speedy Net. Please remove friends before you proceed.").format(user_number_of_friends, User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED))

    def check_other_user_friends(self, user):
        other_user_number_of_friends = len(Friend.objects.friends(user=user))
        if (other_user_number_of_friends >= User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED):
            # ~~~~ TODO: this translation may depend also on the other user's gender (it depends on both user genders).
            # ~~~~ TODO: maybe this translation to Hebrew is not correct and depends on the wrong gender.
            # ~~~~ TODO: maybe we need different messages in English too, depends on the gender ("them").
            raise ValidationError(pgettext_lazy(context=user.get_gender(), message="This user already has {0} friends. They can't have more than {1} friends on Speedy Net. Please ask them to remove friends before you proceed.").format(other_user_number_of_friends, User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED))


class FriendshipRequestView(LimitMaxFriendsMixin, UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'friends.request'

    def _you_cannot_be_friends_with_yourself_error_message(self, user):
        return pgettext_lazy(context=user.get_gender(), message="You cannot be friends with yourself.")

    def _you_already_requested_friendship_from_this_user_error_message(self, user):
        return pgettext_lazy(context=user.get_gender(), message="You already requested friendship from this user.")

    def _you_already_are_friends_with_this_user_error_message(self, user):
        return pgettext_lazy(context=user.get_gender(), message="You already are friends with this user.")

    def get(self, request, *args, **kwargs):
        return redirect(to=self.user)

    def dispatch(self, request, *args, **kwargs):
        self.user = self.get_user()
        if (request.user.is_authenticated):
            if (is_self(user=request.user, other_user=self.user)):
                messages.error(request=request, message=self._you_cannot_be_friends_with_yourself_error_message(user=request.user))
                return redirect(to=self.user)
            if (friendship_request_sent(user=request.user, other_user=self.user)):
                messages.warning(request=request, message=self._you_already_requested_friendship_from_this_user_error_message(user=request.user))
                return redirect(to=self.user)
            if (are_friends(user=request.user, other_user=self.user)):
                messages.warning(request=request, message=self._you_already_are_friends_with_this_user_error_message(user=request.user))
                return redirect(to=self.user)
        return super().dispatch(request=request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            self.check_own_friends()
            self.check_other_user_friends(user=self.user)
        except ValidationError as e:
            messages.error(request=self.request, message=e.message)
            return redirect(to=self.user)
        try:
            Friend.objects.add_friend(from_user=request.user, to_user=self.user)
        except (ValidationError, AlreadyExistsError, AlreadyFriendsError) as e:
            message_dict = {
                "Users cannot be friends with themselves.": self._you_cannot_be_friends_with_yourself_error_message(user=request.user),
                "Users are already friends.": self._you_already_are_friends_with_this_user_error_message(user=request.user),
                "Friendship already requested.": self._you_already_requested_friendship_from_this_user_error_message(user=request.user),
            }
            for key in message_dict.keys():
                message_dict[key.replace(".", "")] = message_dict[key]
            message = e.message
            if (message in message_dict):
                message = message_dict[message]
            else:
                message = _(message)
            messages.error(request=self.request, message=message)
            return redirect(to=self.user)
        messages.success(request=request, message=_('Friendship request sent.'))
        return redirect(to=self.user)


class CancelFriendshipRequestView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'friends.cancel_request'

    def post(self, request, *args, **kwargs):
        try:
            friendship_request = FriendshipRequest.objects.get(from_user=self.request.user, to_user=self.user)
        except FriendshipRequest.DoesNotExist:
            messages.error(request=request, message=_('No friendship request.'))
            return redirect(to=self.user)
        friendship_request.cancel()
        messages.success(request=request, message=pgettext_lazy(context=request.user.get_gender(), message="You've cancelled your friendship request."))
        return redirect(to=self.user)


class AcceptRejectFriendshipRequestViewBase(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'friends.view_requests'

    def get_redirect_url(self):
        return reverse('friends:list', kwargs={'slug': self.request.user.slug})

    def get_friendship_request(self):
        if (not (hasattr(self, '_friendship_request'))):
            self._friendship_request = get_object_or_404(self.user.friendship_requests_received, pk=self.kwargs.get('friendship_request_id'))
        return self._friendship_request

    def get(self, request, *args, **kwargs):
        return redirect(to=self.get_redirect_url())

    def post(self, request, *args, **kwargs):
        friendship_request = self.get_friendship_request()
        getattr(friendship_request, self.action)()
        messages.success(request=request, message=self.message)
        return redirect(to=self.get_redirect_url())


class AcceptFriendshipRequestView(LimitMaxFriendsMixin, AcceptRejectFriendshipRequestViewBase):
    action = 'accept'
    message = _('Friendship request accepted.')

    def post(self, request, *args, **kwargs):
        friendship_request = self.get_friendship_request()
        try:
            self.check_own_friends()
            self.check_other_user_friends(user=friendship_request.from_user)
        except ValidationError as e:
            messages.error(request=self.request, message=e.message)
            return redirect(to=self.get_redirect_url())
        return super().post(request=request, *args, **kwargs)


class RejectFriendshipRequestView(AcceptRejectFriendshipRequestViewBase):
    action = 'cancel'
    message = _('Friendship request rejected.')


class RemoveFriendView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'friends.remove'

    def get(self, request, *args, **kwargs):
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        Friend.objects.remove_friend(from_user=self.request.user, to_user=self.user)
        messages.success(request=request, message=pgettext_lazy(context=request.user.get_gender(), message="You have removed this user from your friends."))
        return redirect(to=self.user)


