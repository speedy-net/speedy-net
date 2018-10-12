from django.urls import reverse
from django.shortcuts import redirect
from django.views import generic
from rules.contrib.views import PermissionRequiredMixin

from speedy.core.accounts.models import User
from speedy.core.accounts.utils import get_site_profile_model
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
        cd.update({
            'display': self.display,
        })
        return cd


class LikeListToView(LikeListViewBase):
    display = 'to'

    def get_queryset(self):
        SiteProfile = get_site_profile_model()
        table_name = SiteProfile._meta.db_table

        # filter out users that are only active in another language
        liked_user = User.objects.filter(pk__in=UserLike.objects.filter(from_user=self.user).values_list('to_user_id', flat=True))
        liked_user = [u.pk for u in liked_user if u.profile.is_active]

        return UserLike.objects.filter(from_user=self.user).filter(to_user__in=liked_user).extra(select={
                'last_visit': 'select last_visit from {} where user_id = likes_userlike.to_user_id'.format(
                    table_name),
            }, ).order_by('-last_visit')


class LikeListFromView(LikeListViewBase):
    display = 'from'

    def get_queryset(self):
        SiteProfile = get_site_profile_model()
        table_name = SiteProfile._meta.db_table

        # filter out users that are only active in another language
        who_likes_me = User.objects.filter(pk__in=UserLike.objects.filter(to_user=self.user).values_list('from_user_id', flat=True))
        who_likes_me = [u.pk for u in who_likes_me if u.profile.is_active]

        return UserLike.objects.filter(to_user=self.user).filter(from_user__in=who_likes_me).extra(select={
                'last_visit': 'select last_visit from {} where user_id = likes_userlike.from_user_id'.format(
                    table_name),
            }, ).order_by('-last_visit')


class LikeListMutualView(LikeListViewBase):
    display = 'to'

    def get_queryset(self):
        who_likes_me = User.objects.filter(pk__in=UserLike.objects.filter(to_user=self.user).values_list('from_user_id', flat=True))

        # filter out users that are only active in another language
        who_likes_me = [u.pk for u in who_likes_me if u.profile.is_active]

        SiteProfile = get_site_profile_model()
        table_name = SiteProfile._meta.db_table
        return UserLike.objects.filter(from_user=self.user,
                                         to_user_id__in=who_likes_me).extra(select={
                'last_visit': 'select last_visit from {} where user_id = likes_userlike.to_user_id'.format(
                    table_name),
            }, ).order_by('-last_visit')


class LikeView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'likes.like'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        UserLike.objects.create(from_user=self.request.user, to_user=self.user)
        # messages.success(request=request, message=_('You like this user.'))
        return redirect(to=self.user)


class UnlikeView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'likes.unlike'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        UserLike.objects.filter(from_user=self.request.user, to_user=self.user).delete()
        # messages.success(request=request, message=_('You don\'t like this user.'))
        return redirect(to=self.user)


