from django.conf import settings as django_settings
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.utils.module_loading import import_string
from django.utils.translation import pgettext_lazy
from django.views import generic
from friendship.models import FriendshipRequest
from rules.contrib.views import LoginRequiredMixin

from speedy.core.base.utils import get_both_genders_context_from_users
from speedy.core.friends.rules import friendship_request_sent, friendship_request_received, are_friends
from speedy.core.base.utils import normalize_username
from speedy.core.accounts.models import User

if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
    from speedy.match.likes.rules import you_like_user, user_likes_you


class SelfUserMixin(object):
    """
    Mixin for views that always operate on the currently logged-in user, regardless of any user identifier in the URL.

    Methods:
        get_user(self): Get the currently logged-in user, raising PermissionDenied if not authenticated.
        get_permission_object(self): Get the object used for permission checks (the currently logged-in user).
    """
    def get_user(self):
        """
        Get the currently logged-in user.

        :return: The currently logged-in user.
        :rtype: speedy.core.accounts.models.User
        :raises django.core.exceptions.PermissionDenied: If the request's user is not authenticated.
        """
        if (self.request.user.is_authenticated):
            user = self.request.user
        else:
            raise PermissionDenied()
        return user

    def get_permission_object(self):
        """
        Get the object used for permission checks.

        :return: The currently logged-in user.
        :rtype: speedy.core.accounts.models.User
        """
        return self.get_user()


class UserMixin(object):
    """
    Mixin for views that operate on a user identified by a slug/username/id URL keyword argument, falling back to the request's user when no such argument is present.

    Attributes:
        user_slug_kwarg (str): The name of the URL keyword argument holding the user's slug.

    Methods:
        use_request_user(self): Check whether the view should use the request's user instead of looking up a user from the URL.
        render_to_response(self, context, **response_kwargs): Render the response, returning a 404 status if the viewer lacks permission to view the profile.
        dispatch(self, request, *args, **kwargs): Resolve the user, redirecting permanently to the canonical slug if needed, then dispatch the request.
        get_user_queryset(self): Get the queryset of users eligible to be looked up (all users for staff superusers, active users otherwise).
        get_user(self): Get the user the view operates on, from the request's user or by looking up the URL's slug/username/id.
        get_permission_object(self): Get the object used for permission checks (the resolved user).
        get_context_data(self, **kwargs): Get the context data for the view, including the user and, if authenticated, friendship and (on Speedy Match) like information.
    """
    user_slug_kwarg = 'slug'

    def use_request_user(self):
        """
        Check whether the view should use the request's user instead of looking up a user from the URL.

        :return: True if the URL has no user slug keyword argument, False otherwise.
        :rtype: bool
        """
        return (self.user_slug_kwarg not in self.kwargs)

    def render_to_response(self, context, **response_kwargs):
        """
        Render the response, returning a 404 status if the viewer lacks permission to view the profile.

        :param context: The context data for the response.
        :type context: dict
        :param response_kwargs: Additional keyword arguments for the response.
        :return: The rendered response.
        :rtype: django.http.HttpResponse
        """
        if (not (self.request.user.has_perm(perm='accounts.view_profile', obj=self.get_user()))):
            response_kwargs['status'] = 404
        return super().render_to_response(context=context, **response_kwargs)

    def dispatch(self, request, *args, **kwargs):
        """
        Resolve the user for this request, redirecting permanently to the canonical slug if the URL's slug doesn't match it, then dispatch the request.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The HTTP response.
        :rtype: django.http.HttpResponse
        """
        self.user = self.get_user()
        if ((not (self.use_request_user())) and (self.user.slug != kwargs[self.user_slug_kwarg])):
            kwargs[self.user_slug_kwarg] = self.user.slug
            components = []
            components.extend(request.resolver_match.namespaces)
            components.append(request.resolver_match.url_name)
            return redirect(to=':'.join(components), permanent=True, *args, **kwargs)
        return super().dispatch(request=request, *args, **kwargs)

    def get_user_queryset(self):
        """
        Get the queryset of users eligible to be looked up by slug/username/id.

        :return: All users if the viewer is a staff superuser, active users only otherwise.
        :rtype: django.db.models.QuerySet
        """
        # If the viewer is not admin, show only active users.
        if (self.request.user.is_authenticated):
            if ((self.request.user.is_staff) and (self.request.user.is_superuser)):
                return User.objects.get_queryset()
        return User.objects.active()

    def get_user(self):
        """
        Get the user the view operates on: the request's user if no slug argument is present or the slug is 'me', or the user matching the URL's slug/username/id otherwise.

        :return: The user the view operates on.
        :rtype: speedy.core.accounts.models.User
        :raises django.core.exceptions.PermissionDenied: If the request's user is not authenticated but is required.
        :raises django.http.Http404: If no user matches the URL's slug/username/id.
        """
        slug = self.kwargs.get(self.user_slug_kwarg)
        if ((self.use_request_user()) or (slug == 'me')):
            if (self.request.user.is_authenticated):
                user = self.request.user
            else:
                raise PermissionDenied()
        else:
            users = self.get_user_queryset().filter(Q(slug=slug) | Q(username=normalize_username(username=slug)) | Q(id=slug))
            if (len(users) == 1):
                user = users[0]
                # Users have cached properties, so we don't want to load them to memory twice.
                if (self.request.user.is_authenticated):
                    if (user == self.request.user):
                        user = self.request.user
            else:
                raise Http404()
        return user

    def get_permission_object(self):
        """
        Get the object used for permission checks.

        :return: The resolved user.
        :rtype: speedy.core.accounts.models.User
        """
        return self.get_user()

    def get_context_data(self, **kwargs):
        """
        Get the context data for the view, including the user and, if the viewer is authenticated, friendship information and (on Speedy Match) like information.

        :param kwargs: Additional keyword arguments.
        :return: The context data for the view.
        :rtype: dict
        """
        cd = super().get_context_data(**kwargs)
        cd.update({
            'user': self.user,
        })
        if (self.request.user.is_authenticated):
            cd.update({
                'user_is_friend': are_friends(user=self.request.user, other_user=self.user),
                'friendship_request_sent': friendship_request_sent(user=self.request.user, other_user=self.user),
                'friendship_request_received': friendship_request_received(user=self.request.user, other_user=self.user),
            })
            if (cd['friendship_request_received']):
                friendship_request_received_id = FriendshipRequest.objects.get(from_user=self.user, to_user=self.request.user).pk
                cd.update({
                    'friendship_request_received_id': friendship_request_received_id,
                })
            if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                cd.update({
                    'you_like_user': you_like_user(user=self.request.user, other_user=self.user),
                    'user_likes_you': user_likes_you(user=self.request.user, other_user=self.user),
                    'this_user_doesnt_match_your_profile_message': pgettext_lazy(context=get_both_genders_context_from_users(user=self.request.user, other_user=self.user), message="This user doesn't match your profile, but you can visit their Speedy Net profile. View user's profile on Speedy Net."),
                })
        return cd


class MeView(LoginRequiredMixin, generic.RedirectView):
    """
    View that redirects a logged-in user from /me/ (optionally followed by a sub-path) to their own profile page.

    Methods:
        get_redirect_url(self, *args, **kwargs): Get the redirect URL to the current user's profile page, with any extra path appended.
    """
    def get_redirect_url(self, *args, **kwargs):
        """
        Get the redirect URL to the current user's profile page, with any extra path appended.

        :param kwargs: Additional keyword arguments; may include 'rest', the path to append after the user's profile URL.
        :param args: Additional positional arguments.
        :return: The redirect URL.
        :rtype: str
        """
        url = self.request.user.get_absolute_url()
        rest = kwargs.get('rest')
        if (rest):
            url += '/' + rest
        return url


class UserDetailView(UserMixin, generic.TemplateView):
    """
    View rendering a user's profile detail page, including the configured profile widgets.

    Attributes:
        template_name (str): The template used to render the user's profile detail page.

    Methods:
        get_widget_kwargs(self): Get the keyword arguments used to instantiate each profile widget.
        get_widgets(self): Instantiate all profile widgets configured in USER_PROFILE_WIDGETS.
        get_context_data(self, **kwargs): Get the context data for the view, including the instantiated widgets.
    """
    template_name = 'profiles/user_detail.html'

    def get_widget_kwargs(self):
        """
        Get the keyword arguments used to instantiate each profile widget.

        :return: A dict with the request, the profile's user, and the viewer.
        :rtype: dict
        """
        return {
            'request': self.request,
            'user': self.user,
            'viewer': self.request.user,
        }

    def get_widgets(self):
        """
        Instantiate all profile widgets configured in the USER_PROFILE_WIDGETS setting.

        :return: A list of instantiated widgets.
        :rtype: list
        """
        widgets = []
        for widget_path in django_settings.USER_PROFILE_WIDGETS:
            widget_class = import_string(dotted_path=widget_path)
            widgets.append(widget_class(**self.get_widget_kwargs()))
        return widgets

    def get_context_data(self, **kwargs):
        """
        Get the context data for the view, including the instantiated profile widgets.

        :param kwargs: Additional keyword arguments.
        :return: The context data for the view.
        :rtype: dict
        """
        cd = super().get_context_data(**kwargs)
        cd.update({
            'widgets': self.get_widgets(),
        })
        return cd


