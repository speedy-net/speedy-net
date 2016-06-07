from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'gender', 'date_of_birth')

    @property
    def helper(self):
        helper = FormHelper()
        helper.add_input(Submit('submit', 'Create an account'))
        return helper
