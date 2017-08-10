from rules.contrib.views import LoginRequiredMixin

from speedy.core.profiles.views import MeView, UserDetailView as CoreUserDetailView


class UserDetailView(LoginRequiredMixin, CoreUserDetailView):
    pass


