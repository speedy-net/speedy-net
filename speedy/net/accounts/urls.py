from django.conf.urls import url
from django.views.generic import TemplateView

from speedy.net.accounts.views import RegistrationView

urlpatterns = [
    url('^register/$', RegistrationView.as_view(), name='registration'),
    url('^register/success/$', TemplateView.as_view(template_name='accounts/registration_success.html'),
        name='registration_success'),
]
