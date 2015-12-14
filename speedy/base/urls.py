from django.conf.urls import url, patterns

from . import views

app_name = 'base'
urlpatterns = [
    url(r'^login/$', views.Login.as_view(), name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^activate_email/$', views.activate_email, name='activate_email'),
    url(r'^password_reset_confirm/$', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    url(r'^password_reset/$', views.PasswordReset.as_view(), name='password_reset'),
    url(r'^profile/$', views.BaseProfile.as_view(), name='user_profile'),
    url(r'^add_email/$', views.AddEmail.as_view(), name='add_email'),
]
