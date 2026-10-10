"""
Views for the friends app of Speedy Core: friend lists, sent and received friendship requests, and sending, cancelling, accepting, rejecting and removing friendships.
"""
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils import formats
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.views import generic

from friendship.models import Friend, FriendshipRequest
from friendship.exceptions import AlreadyExistsError, AlreadyFriendsError

from rules.contrib.views import PermissionRequiredMixin

from speedy.core.base.utils import get_both_genders_context_from_users
from speedy.core.base.views import PaginationMixin
from speedy.core.accounts.models import User
from speedy.core.profiles.views import UserMixin
from .rules import is_self, friendship_request_sent, friendship_request_received, are_friends


class FriendsMixin(PaginationMixin):
    """
    Mixin to paginate friends views.
    """
    page_size = 24
    paginate_by = page_size


class UserFriendListView(UserMixin, PermissionRequiredMixin, FriendsMixin, generic.TemplateView):
    """
    View a list of friends in the current site.
    In Speedy Net, only active users.
    In Speedy Match, only active users who match the current user and is dependent on language.
    """
    template_name = 'friends/friend_list.html'
    permission_required = 'friends.view_friend_list'

    def redirect_on_exception(self):
        """
        Return the redirect response used when an error occurs while loading the friend list page.

        :return: A redirect response to the friend list page of the user.
        :rtype: django.http.HttpResponseRedirect
        """
        return redirect(to='friends:list', slug=self.user.slug)

    def get_object_list(self):
        """
        Return the list of objects to paginate for this view.

        :return: The user's list of friends on the current site.
        :rtype: list
        """
        return self.user.site_friends

    def get_context_data(self, **kwargs):
        """
        Return the context data for rendering the friend list page.

        :param kwargs: Additional keyword arguments.
        :return: The context data, including the current page's list of friends.
        :rtype: dict
        """
        cd = super().get_context_data(**kwargs)
        cd.update({
            'friends': self.page.object_list,
        })
        return cd


class ReceivedFriendshipRequestsListView(UserMixin, PermissionRequiredMixin, FriendsMixin, generic.TemplateView):
    """
    View a list of received friendship requests in the current site.
    In Speedy Net, only active users.
    In Speedy Match, only active users who match the current user and is dependent on language.
    """
    template_name = 'friends/received_requests.html'
    permission_required = 'friends.view_requests'

    def redirect_on_exception(self):
        """
        Return the redirect response used when an error occurs while loading the received friendship requests page.

        :return: A redirect response to the received friendship requests page of the user.
        :rtype: django.http.HttpResponseRedirect
        """
        return redirect(to='friends:received_requests', slug=self.user.slug)

    def get_object_list(self):
        """
        Return the list of objects to paginate for this view.

        :return: The user's list of received friendship requests.
        :rtype: list
        """
        return self.user.received_friendship_requests

    def get_context_data(self, **kwargs):
        """
        Return the context data for rendering the received friendship requests page.

        :param kwargs: Additional keyword arguments.
        :return: The context data, including the current page's list of received friendship requests.
        :rtype: dict
        """
        cd = super().get_context_data(**kwargs)
        cd.update({
            'received_friendship_requests': self.page.object_list,
        })
        return cd


class SentFriendshipRequestsListView(UserMixin, PermissionRequiredMixin, FriendsMixin, generic.TemplateView):
    """
    View a list of sent friendship requests in the current site.
    In Speedy Net, only active users.
    In Speedy Match, only active users who match the current user and is dependent on language.
    """
    template_name = 'friends/sent_requests.html'
    permission_required = 'friends.view_requests'

    def redirect_on_exception(self):
        """
        Return the redirect response used when an error occurs while loading the sent friendship requests page.

        :return: A redirect response to the sent friendship requests page of the user.
        :rtype: django.http.HttpResponseRedirect
        """
        return redirect(to='friends:sent_requests', slug=self.user.slug)

    def get_object_list(self):
        """
        Return the list of objects to paginate for this view.

        :return: The user's list of sent friendship requests.
        :rtype: list
        """
        return self.user.sent_friendship_requests

    def get_context_data(self, **kwargs):
        """
        Return the context data for rendering the sent friendship requests page.

        :param kwargs: Additional keyword arguments.
        :return: The context data, including the current page's list of sent friendship requests.
        :rtype: dict
        """
        cd = super().get_context_data(**kwargs)
        cd.update({
            'sent_friendship_requests': self.page.object_list,
        })
        return cd


class LimitMaxFriendsMixin(object):
    """
    Mixin to limit max friends in Speedy Net.
    In Speedy Net, all users, active and not active.
    """
    def check_own_friends(self):
        """
        Raise a validation error if the current logged-in user already has the maximum number of friends allowed on Speedy Net.

        :raises django.core.exceptions.ValidationError: If the user already has the maximum number of friends allowed.
        """
        user_all_friends_count = self.request.user.friends.count()
        if (user_all_friends_count >= User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED):
            raise ValidationError(pgettext_lazy(context=self.request.user.get_gender(), message="You already have {0} friends. You can't have more than {1} friends on Speedy Net. Please remove friends before you proceed.").format(
                formats.number_format(value=user_all_friends_count),
                formats.number_format(value=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED),
            ))

    def check_other_user_friends(self, user):
        """
        Raise a validation error if the given user already has the maximum number of friends allowed on Speedy Net.

        :param user: The other user to check.
        :type user: speedy.core.accounts.models.User
        :raises django.core.exceptions.ValidationError: If the other user already has the maximum number of friends allowed.
        """
        other_user_all_friends_count = user.friends.count()
        if (other_user_all_friends_count >= User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED):
            raise ValidationError(pgettext_lazy(context=get_both_genders_context_from_users(user=self.request.user, other_user=user), message="This user already has {0} friends. They can't have more than {1} friends on Speedy Net. Please ask them to remove friends before you proceed.").format(
                formats.number_format(value=other_user_all_friends_count),
                formats.number_format(value=User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED),
            ))


class FriendshipRequestView(LimitMaxFriendsMixin, UserMixin, PermissionRequiredMixin, generic.View):
    """
    Send a friendship request.
    """
    permission_required = 'friends.request'

    def _you_cannot_be_friends_with_yourself_error_message(self, user):
        """
        Return the error message shown when a user tries to send a friendship request to themselves.

        :param user: The user trying to send the friendship request.
        :type user: speedy.core.accounts.models.User
        :return: The error message.
        :rtype: str
        """
        return pgettext_lazy(context=user.get_gender(), message="You cannot be friends with yourself.")

    def _you_already_requested_friendship_from_this_user_error_message(self, user, other_user):
        """
        Return the error message shown when a user has already requested friendship from the other user.

        :param user: The user who sent the friendship request.
        :type user: speedy.core.accounts.models.User
        :param other_user: The user who received the friendship request.
        :type other_user: speedy.core.accounts.models.User
        :return: The error message.
        :rtype: str
        """
        return pgettext_lazy(context=other_user.get_gender(), message="You already requested friendship from this user.")

    def _this_user_already_requested_friendship_from_you_error_message(self, user, other_user):
        """
        Return the error message shown when the other user has already requested friendship from the current user.

        :param user: The user who would be sending the friendship request.
        :type user: speedy.core.accounts.models.User
        :param other_user: The user who already sent the friendship request.
        :type other_user: speedy.core.accounts.models.User
        :return: The error message.
        :rtype: str
        """
        return pgettext_lazy(context=other_user.get_gender(), message="This user already requested friendship from you.")

    def _you_already_are_friends_with_this_user_error_message(self, user, other_user):
        """
        Return the error message shown when the two users are already friends.

        :param user: The first user.
        :type user: speedy.core.accounts.models.User
        :param other_user: The second user.
        :type other_user: speedy.core.accounts.models.User
        :return: The error message.
        :rtype: str
        """
        return pgettext_lazy(context=get_both_genders_context_from_users(user=user, other_user=other_user), message="You already are friends with this user.")

    def get(self, request, *args, **kwargs):
        """
        Redirect GET requests to the other user's profile page, since friendship requests are only sent via POST.

        :param request: The HTTP request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the other user's profile page.
        :rtype: django.http.HttpResponseRedirect
        """
        return redirect(to=self.user)

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch the request, redirecting with an error or warning message if the user cannot send a friendship request to the other user (themselves, already requested, already received a request, or already friends).

        :param request: The HTTP request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response, or the result of the superclass's dispatch.
        """
        self.user = self.get_user()
        if (request.user.is_authenticated):
            if (is_self(user=request.user, other_user=self.user)):
                messages.error(request=request, message=self._you_cannot_be_friends_with_yourself_error_message(user=request.user))
                return redirect(to=self.user)
            if (friendship_request_sent(user=request.user, other_user=self.user)):
                messages.warning(request=request, message=self._you_already_requested_friendship_from_this_user_error_message(user=request.user, other_user=self.user))
                return redirect(to=self.user)
            if (friendship_request_received(user=request.user, other_user=self.user)):
                messages.warning(request=request, message=self._this_user_already_requested_friendship_from_you_error_message(user=request.user, other_user=self.user))
                return redirect(to=self.user)
            if (are_friends(user=request.user, other_user=self.user)):
                messages.warning(request=request, message=self._you_already_are_friends_with_this_user_error_message(user=request.user, other_user=self.user))
                return redirect(to=self.user)
        return super().dispatch(request=request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Create a friendship request from the current user to the other user, enforcing the maximum friends limit and handling already-existing requests/friendships with an appropriate message.

        :param request: The HTTP request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the other user's profile page.
        :rtype: django.http.HttpResponseRedirect
        """
        try:
            self.check_own_friends()
            self.check_other_user_friends(user=self.user)
        except ValidationError as e:
            messages.error(request=self.request, message=e.message)
            return redirect(to=self.user)
        try:
            if (FriendshipRequest.objects.filter(from_user=request.user, to_user=self.user).exists()):
                raise AlreadyExistsError(self._you_already_requested_friendship_from_this_user_error_message(user=request.user, other_user=self.user))
            if (FriendshipRequest.objects.filter(from_user=self.user, to_user=request.user).exists()):
                raise AlreadyExistsError(self._this_user_already_requested_friendship_from_you_error_message(user=request.user, other_user=self.user))
            Friend.objects.add_friend(from_user=request.user, to_user=self.user)
        except (ValidationError, AlreadyExistsError, AlreadyFriendsError) as e:
            message_dict = {
                "Users cannot be friends with themselves.": self._you_cannot_be_friends_with_yourself_error_message(user=request.user),
                "Users are already friends.": self._you_already_are_friends_with_this_user_error_message(user=request.user, other_user=self.user),
                "Friendship already requested.": self._you_already_requested_friendship_from_this_user_error_message(user=request.user, other_user=self.user),
            }
            for key in list(message_dict.keys()):
                message_dict[key.replace(".", "")] = message_dict[key]
            if (isinstance(e, ValidationError)):
                message = e.message
            else:
                message = str(e)
            if (message in message_dict):
                message = message_dict[message]
            else:
                message = _(message)
            messages.error(request=self.request, message=message)
            return redirect(to=self.user)
        messages.success(request=request, message=_('Friendship request sent.'))
        return redirect(to=self.user)


class CancelFriendshipRequestView(UserMixin, PermissionRequiredMixin, generic.View):
    """
    Cancel a friendship request.
    """
    permission_required = 'friends.cancel_request'

    def post(self, request, *args, **kwargs):
        """
        Cancel the friendship request sent by the current user to the other user, if one exists.

        :param request: The HTTP request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the other user's profile page.
        :rtype: django.http.HttpResponseRedirect
        """
        friendship_requests = FriendshipRequest.objects.filter(from_user=self.request.user, to_user=self.user)
        if (len(friendship_requests) == 1):
            friendship_request = friendship_requests[0]
        else:
            messages.error(request=request, message=_('No friendship request.'))
            return redirect(to=self.user)
        friendship_request.cancel()
        messages.success(request=request, message=pgettext_lazy(context=request.user.get_gender(), message="You've cancelled your friendship request."))
        return redirect(to=self.user)


class AcceptRejectFriendshipRequestViewBase(UserMixin, PermissionRequiredMixin, generic.View):
    """
    Base view to accept or reject a friendship request.
    """
    permission_required = 'friends.view_requests'

    def get_redirect_url(self):
        """
        Return the URL to redirect to after accepting or rejecting the friendship request.

        :return: The absolute URL of the user who sent the request, or the friend list URL if there is no such user.
        :rtype: str
        """
        if (hasattr(self, '_user_who_sent_the_request')):
            return self._user_who_sent_the_request.get_absolute_url()
        return reverse(viewname='friends:list', kwargs={'slug': self.request.user.slug})

    def get_friendship_request(self):
        """
        Return the friendship request to accept or reject, as identified by the ``friendship_request_id`` URL keyword argument, caching the result and the sending user on ``self``.

        :return: The friendship request.
        :rtype: friendship.models.FriendshipRequest
        :raises django.http.Http404: If no such friendship request was received by the user.
        """
        if (not (hasattr(self, '_friendship_request'))):
            self._friendship_request = get_object_or_404(klass=self.user.friendship_requests_received, pk=self.kwargs.get('friendship_request_id'))
            self._user_who_sent_the_request = self._friendship_request.from_user
        return self._friendship_request

    def get(self, request, *args, **kwargs):
        """
        Redirect GET requests, since accepting/rejecting a friendship request is only done via POST.

        :param request: The HTTP request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the redirect URL.
        :rtype: django.http.HttpResponseRedirect
        """
        return redirect(to=self.get_redirect_url())

    def post(self, request, *args, **kwargs):
        """
        Perform ``self.action`` (accept or reject) on the friendship request and show the corresponding success message.

        :param request: The HTTP request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the redirect URL.
        :rtype: django.http.HttpResponseRedirect
        """
        friendship_request = self.get_friendship_request()
        getattr(friendship_request, self.action)()
        messages.success(request=request, message=self.message)
        return redirect(to=self.get_redirect_url())


class AcceptFriendshipRequestView(LimitMaxFriendsMixin, AcceptRejectFriendshipRequestViewBase):
    """
    Accept a friendship request.
    """
    action = 'accept'
    message = _('Friendship request accepted.')

    def post(self, request, *args, **kwargs):
        """
        Accept the friendship request, enforcing the maximum friends limit for both the current user and the user who sent the request.

        :param request: The HTTP request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the redirect URL.
        :rtype: django.http.HttpResponseRedirect
        """
        friendship_request = self.get_friendship_request()
        try:
            self.check_own_friends()
            self.check_other_user_friends(user=friendship_request.from_user)
        except ValidationError as e:
            messages.error(request=self.request, message=e.message)
            return redirect(to=self.get_redirect_url())
        return super().post(request=request, *args, **kwargs)


class RejectFriendshipRequestView(AcceptRejectFriendshipRequestViewBase):
    """
    Reject a friendship request.
    """
    action = 'cancel'
    message = _('Friendship request rejected.')


class RemoveFriendView(UserMixin, PermissionRequiredMixin, generic.View):
    """
    Remove a friend.
    """
    permission_required = 'friends.remove'

    def get(self, request, *args, **kwargs):
        """
        Redirect GET requests to the other user's profile page, since removing a friend is only done via POST.

        :param request: The HTTP request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the other user's profile page.
        :rtype: django.http.HttpResponseRedirect
        """
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        """
        Remove the friendship between the current user and the other user.

        :param request: The HTTP request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the other user's profile page.
        :rtype: django.http.HttpResponseRedirect
        """
        Friend.objects.remove_friend(from_user=self.request.user, to_user=self.user)
        messages.success(request=request, message=pgettext_lazy(context=self.user.get_gender(), message="You have removed this user from your friends."))
        return redirect(to=self.user)


