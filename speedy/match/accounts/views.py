from speedy.core.accounts.views import IndexView as CoreIndexView, EditProfileNotificationsView as CoreEditProfileNotificationsView
from .forms import ProfileNotificationsForm


class IndexView(CoreIndexView):
    registered_redirect_to = 'matches:list'


class EditProfileNotificationsView(CoreEditProfileNotificationsView):
    form_class = ProfileNotificationsForm


