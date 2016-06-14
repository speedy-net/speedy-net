from speedy.net.accounts import views as net_views

from . import forms


class EditProfileView(net_views.EditProfileView):
    def get_form_classes(self):
        form_classes = self.form_classes.copy()
        form_classes['privacy'] = forms.AccountPrivacyForm
        return form_classes
