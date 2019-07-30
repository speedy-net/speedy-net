from django.urls import reverse
from django.shortcuts import redirect
from django.views import generic
from django.utils.translation import gettext_lazy as _

from rules.contrib.views import PermissionRequiredMixin

from speedy.core.accounts.models import User
from speedy.core.profiles.views import UserMixin
from .models import UserLike


class LikeListDefaultRedirectView(UserMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('likes:list_to', kwargs={'slug': self.user.slug})


class LikeListViewBase(UserMixin, PermissionRequiredMixin, generic.ListView):
    permission_required = 'likes.view_likes'
    template_name = 'likes/like_list.html'
    paginate_by = 25

    def get_context_data(self, **kwargs):
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
        })
        return cd


class LikeListToView(LikeListViewBase):
    display = 'to'

    def get_queryset(self):
        return UserLike.objects.get_like_list_to_queryset(user=self.user)


class LikeListFromView(LikeListViewBase):
    display = 'from'

    def get_queryset(self):
        return UserLike.objects.get_like_list_from_queryset(user=self.user)


class LikeListMutualView(LikeListViewBase):
    display = 'to'

    def get_queryset(self):
        return UserLike.objects.get_like_list_mutual_queryset(user=self.user)


class LikeView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'likes.like'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        UserLike.objects.add_like(from_user=self.request.user, to_user=self.user)
        return redirect(to=self.user)


class UnlikeView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'likes.unlike'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        UserLike.objects.remove_like(from_user=self.request.user, to_user=self.user)
        return redirect(to=self.user)


