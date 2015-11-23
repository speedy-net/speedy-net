from registration.forms import RegistrationForm
from django import forms

from base.models import UserProfile


class UserProfileForm(RegistrationForm):
    """ Custom form for the registration page.

        let RegistrationForm save the user model. TODO: change widget of the user fields to use bootstrap.
        save new UserProfile for the new user.
    """
    class Media:
        # add styles for the form
        css = {
            'all': ['registration/register.css']
        }

    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_of_birth = forms.DateTimeField(input_formats=['%d-%m-%Y %H:%M'], widget=forms.TextInput(attrs={'class': 'form-control'}))
    profile_picture = forms.ImageField(required=False)

    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    diet = forms.ChoiceField(choices=UserProfile.DIET_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    security_question = forms.ChoiceField(choices=UserProfile.SECURITY_QUESTIONS, widget=forms.Select(attrs={'class': 'form-control'}))
    security_answer = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))


    def clean_date_of_birth(self):
        return self.cleaned_data['date_of_birth']

    def save(self, *args, **kwargs):
        user = super(UserProfileForm, self).save(*args, **kwargs)

        data = self.cleaned_data
        files = self.files

        if data.get('first_name', None):
            user.first_name = data['first_name']
        if data.get('last_name'):
            user.last_name = data['last_name']
        user.set_password(data['password1'])
        user.save()

        profile = UserProfile(
            user=user,
            gender=data['gender'],
            diet=data['diet'],
            date_of_birth=data['date_of_birth'],
            security_question=data['security_question'],
            security_answer=data['security_answer']
        )

        if files.get('profile_picture', None):
            profile.profile_picture = files['profile_picture']

        profile.save()
        return user
