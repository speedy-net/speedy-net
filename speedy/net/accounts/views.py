from speedy.core.accounts.views import IndexView as CoreIndexView


class IndexView(CoreIndexView):
    registered_redirect_to = 'profiles:me'


