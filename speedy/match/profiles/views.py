from rules.contrib.views import LoginRequiredMixin

from speedy.core.profiles import views as speedy_core_profiles_views


class UserDetailView(LoginRequiredMixin, speedy_core_profiles_views.UserDetailView):
    """
    Speedy Match user profile detail view, requiring the viewer to be authenticated.
    """
    pass


