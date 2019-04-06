from django.urls import reverse_lazy

from speedy.core.accounts.views import IndexView as CoreIndexView, ActivateSiteProfileView as CoreActivateSiteProfileView


class IndexView(CoreIndexView):
    registered_redirect_to = 'profiles:me'


class ActivateSiteProfileView(CoreActivateSiteProfileView):
    def get_account_activation_url(self):
        return reverse_lazy('accounts:activate')


