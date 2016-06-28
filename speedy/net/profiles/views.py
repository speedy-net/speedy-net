from django.http import Http404
from django.views import generic
from rules.contrib.views import LoginRequiredMixin

from speedy.net.accounts.models import User
from speedy.net.friends.rules import friend_request_sent, users_are_friends


class UserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.user = self.get_user()
        return super().dispatch(request, *args, **kwargs)

    def get_user(self):
        try:
            return User.objects.active().get(slug__iexact=self.kwargs.get('username'))
        except:
            raise Http404()

    def get_permission_object(self):
        return self.get_user()

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'user': self.user,
        })
        if self.request.user.is_authenticated():
            cd.update({
                'user_is_friend': users_are_friends(self.request.user, self.user),
                'friend_request_sent': friend_request_sent(self.request.user, self.user),
            })
        return cd


class MeView(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        url = self.request.user.get_absolute_url()
        rest = kwargs.get('rest')
        if rest:
            url += '/' + rest
        return url


class UserDetailView(UserMixin, generic.TemplateView):
    template_name = 'profiles/user_detail.html'
