from django.urls import re_path
from django.contrib.auth import views as auth_views
from django.views import generic
from django.urls import reverse_lazy

from . import forms
from . import views

app_name = 'speedy.core.accounts'
urlpatterns = [
    re_path(route=r'^set-session/$', view=views.set_session, name='set_session'),

    re_path(route=r'^login/$', view=auth_views.LoginView.as_view(template_name='accounts/login.html', authentication_form=forms.LoginForm, extra_context=None), name='login'),
    re_path(route=r'^logout/$', view=auth_views.LogoutView.as_view(template_name='accounts/logged_out.html'), name='logout'),

    re_path(route=r'^reset-password/$', view=auth_views.PasswordResetView.as_view(template_name='accounts/password_reset/form.html', form_class=forms.PasswordResetForm, success_url=reverse_lazy('accounts:password_reset_done')), name='password_reset'),
    re_path(route=r'^reset-password/done/$', view=generic.TemplateView.as_view(template_name='accounts/password_reset/done.html'), name='password_reset_done'),
    re_path(route=r'^reset-password/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', view=auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset/confirm.html', form_class=forms.SetPasswordForm, success_url=reverse_lazy('accounts:password_reset_complete')), name='password_reset_confirm'),
    re_path(route=r'^reset-password/complete/$', view=auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset/complete.html'), name='password_reset_complete'),

    re_path(route=r'^edit-profile/$', view=views.EditProfileView.as_view(), name='edit_profile'),
    re_path(route=r'^edit-profile/privacy/$', view=views.EditProfilePrivacyView.as_view(), name='edit_profile_privacy'),
    re_path(route=r'^edit-profile/credentials/$', view=views.EditProfileCredentialsView.as_view(), name='edit_profile_credentials'),
    re_path(route=r'^edit-profile/deactivate/$', view=views.DeactivateSiteProfileView.as_view(), name='deactivate_profile'),
    re_path(route=r'^edit-profile/emails/$', view=generic.RedirectView.as_view(pattern_name='accounts:edit_profile_credentials'), name='edit_profile_emails'),
    re_path(route=r'^edit-profile/emails/(?P<pk>\d+)/verify/(?P<token>\w+)/$', view=views.VerifyUserEmailAddressView.as_view(), name='verify_email'),
    re_path(route=r'^edit-profile/emails/add/$', view=views.AddUserEmailAddressView.as_view(), name='add_email'),
    re_path(route=r'^edit-profile/emails/(?P<pk>\d+)/confirm/$', view=views.ResendConfirmationEmailView.as_view(), name='confirm_email'),
    re_path(route=r'^edit-profile/emails/(?P<pk>\d+)/delete/$', view=views.DeleteUserEmailAddressView.as_view(), name='delete_email'),
    re_path(route=r'^edit-profile/emails/(?P<pk>\d+)/set-primary/$', view=views.SetPrimaryUserEmailAddressView.as_view(), name='set_primary_email'),
    re_path(route=r'^edit-profile/emails/(?P<pk>\d+)/privacy/$', view=views.ChangeUserEmailAddressPrivacyView.as_view(), name='change_email_privacy'),
]


