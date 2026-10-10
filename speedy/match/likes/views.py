"""
Views for the likes of Speedy Match - the lists of likes to, from and mutual likes of a user, and the like and unlike views.
"""
from django.urls import reverse
from django.shortcuts import redirect
from django.views import generic
from django.utils.translation import gettext_lazy as _

from rules.contrib.views import PermissionRequiredMixin

from speedy.core.accounts.models import User
from speedy.core.profiles.views import UserMixin
from .models import UserLike


class LikeListDefaultRedirectView(UserMixin, generic.RedirectView):
    """
    Redirects to the default likes list view (likes given by the user) for a user's slug.

    Methods:
        get_redirect_url(self, *args, **kwargs): Returns the URL of the "likes to" list view for the user.
    """
    def get_redirect_url(self, *args, **kwargs):
        """
        Returns the URL of the "likes given" list view for the current user.

        :param args: Positional arguments (unused).
        :param kwargs: Keyword arguments (unused).
        :return: The redirect URL.
        :rtype: str
        """
        return reverse(viewname='likes:list_to', kwargs={'slug': self.user.slug})


class LikeListViewBase(UserMixin, PermissionRequiredMixin, generic.ListView):
    """
    Base view for the likes list pages (likes given, likes received, mutual likes), building the gender-aware page titles.

    Methods:
        get_context_data(self, **kwargs): Adds the display mode and gender-aware titles to the context.
    """
    permission_required = 'likes.view_likes'
    template_name = 'likes/like_list.html'
    page_size = 24
    paginate_by = page_size

    def get_context_data(self, **kwargs):
        """
        Adds the display mode, gender-aware list titles and the like list to the template context.

        :param kwargs: Additional keyword arguments.
        :return: The context data.
        :rtype: dict
        """
        cd = super().get_context_data(**kwargs)
        user_like_gender = self.user.speedy_match_profile.get_like_gender()
        list_to_title = {
            User.GENDER_FEMALE_STRING: _('Girls You Like'),
            User.GENDER_MALE_STRING: _('Boys You Like'),
            User.GENDER_OTHER_STRING: _('People You Like'),
        }[user_like_gender]
        list_from_title = {
            User.GENDER_FEMALE_STRING: _('Girls Who Like You'),
            User.GENDER_MALE_STRING: _('Boys Who Like You'),
            User.GENDER_OTHER_STRING: _('People Who Like You'),
        }[user_like_gender]
        list_mutual_title = _('Mutual Likes')
        cd.update({
            'display': self.display,
            'list_to_title': list_to_title,
            'list_from_title': list_from_title,
            'list_mutual_title': list_mutual_title,
            'like_list': cd['object_list'],
        })
        return cd


class LikeListToView(LikeListViewBase):
    """
    Lists the users that the viewed user likes.

    Methods:
        get_queryset(self): Returns the queryset of likes given by the user.
    """
    display = 'to'

    def get_queryset(self):
        """
        Returns the queryset of likes given by the user.

        :return: The queryset of UserLike instances.
        :rtype: django.db.models.QuerySet
        """
        return UserLike.objects.get_like_list_to_queryset(user=self.user)


class LikeListFromView(LikeListViewBase):
    """
    Lists the users who like the viewed user.

    Methods:
        get_queryset(self): Returns the queryset of likes received by the user.
    """
    display = 'from'

    def get_queryset(self):
        """
        Returns the queryset of likes received by the user.

        :return: The queryset of UserLike instances.
        :rtype: django.db.models.QuerySet
        """
        return UserLike.objects.get_like_list_from_queryset(user=self.user)


class LikeListMutualView(LikeListViewBase):
    """
    Lists the users who mutually like the viewed user.

    Methods:
        get_queryset(self): Returns the queryset of mutual likes.
    """
    display = 'to'

    def get_queryset(self):
        """
        Returns the queryset of mutual likes for the user.

        :return: The queryset of UserLike instances.
        :rtype: django.db.models.QuerySet
        """
        return UserLike.objects.get_like_list_mutual_queryset(user=self.user)


class LikeView(UserMixin, PermissionRequiredMixin, generic.View):
    """
    Handles creating a like from the requesting user to the viewed user.

    Methods:
        get(self, request, *args, **kwargs): Redirects to the viewed user's profile without creating a like.
        post(self, request, *args, **kwargs): Creates the like and redirects to the viewed user's profile.
    """
    permission_required = 'likes.like'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        """
        Redirects to the viewed user's profile without creating a like.

        :param request: The HTTP request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the viewed user's profile.
        """
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        """
        Creates a like from the requesting user to the viewed user and redirects to the viewed user's profile.

        :param request: The HTTP request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the viewed user's profile.
        """
        UserLike.objects.add_like(from_user=self.request.user, to_user=self.user)
        return redirect(to=self.user)


class UnlikeView(UserMixin, PermissionRequiredMixin, generic.View):
    """
    Handles removing a like from the requesting user to the viewed user.

    Methods:
        get(self, request, *args, **kwargs): Redirects to the viewed user's profile without removing the like.
        post(self, request, *args, **kwargs): Removes the like and redirects to the viewed user's profile.
    """
    permission_required = 'likes.unlike'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        """
        Redirects to the viewed user's profile without removing the like.

        :param request: The HTTP request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the viewed user's profile.
        """
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        """
        Removes the like from the requesting user to the viewed user and redirects to the viewed user's profile.

        :param request: The HTTP request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the viewed user's profile.
        """
        UserLike.objects.remove_like(from_user=self.request.user, to_user=self.user)
        return redirect(to=self.user)


