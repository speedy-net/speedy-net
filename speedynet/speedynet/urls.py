from django.conf.urls import include, url
from django.contrib import admin

from registration.backends.default.views import RegistrationView

from base.forms import UserProfileForm
from base.views import *

urlpatterns = [
    # admin
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # custom registration form
    url(r'^accounts/register/$', RegistrationView.as_view(form_class=UserProfileForm), name='registration_register'),
    # base user profile
    url(r'^accounts/profile/$', ProfileView.as_view(), name='user_profile'),
    # registration urls
    url(r'^accounts/', include('registration.backends.default.urls')),
    # custom password confirm url - grappelli conflicts
    url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm', {'template_name': 'registration/password_reset_confirm.html'}, name="password_reset_confirm"),
    # django auth urls - for password change
    url(r'^accounts/', include('django.contrib.auth.urls')),

    # other urls
]
