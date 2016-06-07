from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^me/$', views.MeView.as_view(), name='me'),
    url(r'^register/$', views.RegistrationView.as_view(), name='registration'),
    url(r'^register/success/$', TemplateView.as_view(template_name='accounts/registration_success.html'),
        name='registration_success'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout', kwargs={'template_name': 'accounts/logged_out.html'}),
    url(r'^(?P<slug>[-\w]+)/', views.UserProfileView.as_view(), name='user_profile'),
]
