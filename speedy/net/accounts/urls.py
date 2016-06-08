from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views import generic

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^register/$', views.RegistrationView.as_view(), name='registration'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout', kwargs={'template_name': 'accounts/logged_out.html'}),
    url(r'^me/$', views.MeView.as_view(), name='me'),
    url(r'^edit-profile/$', views.EditProfileView.as_view(), name='edit_profile'),
    url(r'^edit-profile/emails/$', generic.RedirectView.as_view(pattern_name='accounts:edit_profile'),
        name='edit_profile_emails'),
    url(r'^edit-profile/emails/verify/(?P<token>\w+)/$', views.VerifyUserEmailAddressView.as_view(), name='verify_email'),
    url(r'^edit-profile/emails/add/$', views.AddUserEmailAddressView.as_view(), name='add_email'),
    url(r'^edit-profile/emails/(?P<pk>\d+)/confirm/$', views.ResendConfirmationEmailView.as_view(),
        name='confirm_email'),
    url(r'^edit-profile/emails/(?P<pk>\d+)/delete/$', views.DeleteUserEmailAddressView.as_view(),
        name='delete_email'),
    url(r'^edit-profile/emails/(?P<pk>\d+)/set-primary/$', views.SetPrimaryUserEmailAddressView.as_view(),
        name='set_primary_email'),
    url(r'^(?P<slug>[-\w]+)/', views.UserProfileView.as_view(), name='user_profile'),
]
