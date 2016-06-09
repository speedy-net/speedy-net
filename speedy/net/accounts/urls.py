from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views import generic

from . import forms
from . import views

urlpatterns = [

    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^me/$', views.MeView.as_view(), name='me'),

    url(r'^register/$', views.RegistrationView.as_view(), name='registration'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout', kwargs={'template_name': 'accounts/logged_out.html'}),

    url(r'^reset-password/$',
        auth_views.password_reset,
        {'post_reset_redirect': 'accounts:password_reset_done',
         'template_name': 'accounts/password_reset_form.html',
         'email_template_name': 'accounts/email/password_reset_body.txt',
         'html_email_template_name': 'accounts/password_reset_body.html',
         'password_reset_form': forms.PasswordResetForm},
        name='password_reset'),

    url(r'^reset-password/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {'post_reset_redirect': 'accounts:password_reset_complete',
         'set_password_form': forms.SetPasswordForm,
         'template_name': 'accounts/password_reset_confirm.html'},
        name='password_reset_confirm'),

    url(r'^reset-password/complete/$',
        auth_views.password_reset_complete,
        {'template_name': 'accounts/password_reset_complete.html'},
        name='password_reset_complete'),

    url(r'^reset-password/done/$',
        auth_views.password_reset_done,
        {'template_name': 'accounts/password_reset_done.html'},
        name='password_reset_done'),

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
