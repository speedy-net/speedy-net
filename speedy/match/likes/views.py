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
        to_like_gender = UserLike.objects.get_to_like_gender(user=self.user)
        from_like_gender = UserLike.objects.get_from_like_gender(user=self.user)
        list_to_title = {
            User.GENDER_FEMALE_STRING: _('Girls You Like'),
            User.GENDER_MALE_STRING: _('Boys You Like'),
            User.GENDER_OTHER_STRING: _('People You Like'),
        }[to_like_gender]
        list_from_title = {
            User.GENDER_FEMALE_STRING: _('Girls Who Like You'),
            User.GENDER_MALE_STRING: _('Boys Who Like You'),
            User.GENDER_OTHER_STRING: _('People Who Like You'),
        }[from_like_gender]
        list_mutual_title = _('Mutual Likes')
        cd.update({
            'display': self.display,
            'list_to_title': list_to_title,
            'list_from_title': list_from_title,
            'list_mutual_title': list_mutual_title,
            'to_like_gender': to_like_gender,
            'from_like_gender': from_like_gender,
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
        UserLike.objects.create(from_user=self.request.user, to_user=self.user)
        return redirect(to=self.user)


class UnlikeView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'likes.unlike'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        UserLike.objects.filter(from_user=self.request.user, to_user=self.user).delete()
        return redirect(to=self.user)


