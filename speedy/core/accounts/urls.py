from django.urls import path

from . import views

app_name = 'speedy.core.accounts'
urlpatterns = [
    path(route='set-session/', view=views.set_session, name='set_session'),

    path(route='login/', view=views.LoginView.as_view(), name='login'),
    path(route='logout/', view=views.LogoutView.as_view(), name='logout'),

    path(route='reset-password/', view=views.PasswordResetView.as_view(), name='password_reset'),
    path(route='reset-password/done/', view=views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path(route='reset-password/confirm/<str:uidb64>/<str:token>/', view=views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path(route='reset-password/complete/', view=views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path(route='edit-profile/', view=views.EditProfileView.as_view(), name='edit_profile'),
    path(route='edit-profile/privacy/', view=views.EditProfilePrivacyView.as_view(), name='edit_profile_privacy'),
    path(route='edit-profile/credentials/', view=views.EditProfileCredentialsView.as_view(), name='edit_profile_credentials'),
    path(route='edit-profile/deactivate/', view=views.DeactivateSiteProfileView.as_view(), name='deactivate_profile'),
    path(route='edit-profile/emails/', view=views.EditProfileEmailsView.as_view(), name='edit_profile_emails'),
    path(route='edit-profile/emails/<digits:pk>/verify/<str:token>/', view=views.VerifyUserEmailAddressView.as_view(), name='verify_email'),
    path(route='edit-profile/emails/add/', view=views.AddUserEmailAddressView.as_view(), name='add_email'),
    path(route='edit-profile/emails/<digits:pk>/confirm/', view=views.ResendConfirmationEmailView.as_view(), name='confirm_email'),
    path(route='edit-profile/emails/<digits:pk>/delete/', view=views.DeleteUserEmailAddressView.as_view(), name='delete_email'),
    path(route='edit-profile/emails/<digits:pk>/set-primary/', view=views.SetPrimaryUserEmailAddressView.as_view(), name='set_primary_email'),
    path(route='edit-profile/emails/<digits:pk>/privacy/', view=views.ChangeUserEmailAddressPrivacyView.as_view(), name='change_email_privacy'),
]


