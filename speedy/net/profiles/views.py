from django.conf import settings
from django.contrib.sites.models import Site
from django.http import Http404
from django.utils.module_loading import import_string
from django.views import generic
from rules.contrib.views import LoginRequiredMixin, PermissionRequiredMixin

from speedy.net.accounts.models import User
from speedy.net.friends.rules import friend_request_sent, is_friend


class UserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.user = self.get_user()
        return super().dispatch(request, *args, **kwargs)

    def get_user_queryset(self):
        return User.objects.active()

    def get_user(self):
        try:
            return self.get_user_queryset().get(slug__iexact=self.kwargs['username'])
        except User.DoesNotExist:
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
                'user_is_friend': is_friend(self.request.user, self.user),
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

    def get_widget_kwargs(self):
        return {
            'entity': self.user,
        }

    def get_widgets(self):
        widgets = []
        for widget_path in settings.USER_PROFILE_WIDGETS:
            widget_class = import_string(widget_path)
            widgets.append(widget_class(**self.get_widget_kwargs()))
        return widgets

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'widgets': self.get_widgets(),
        })
        return cd
