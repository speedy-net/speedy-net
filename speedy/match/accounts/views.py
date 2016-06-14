from speedy.net.accounts import views as net_views

from . import forms


class EditProfilePrivacyView(net_views.EditProfilePrivacyView):
    form_class = forms.AccountPrivacyForm
