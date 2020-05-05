from django.urls import re_path

from . import views

app_name = 'speedy.core.contact_by_email'
urlpatterns = [
    re_path(route=r'^$', view=views.ContactUsView.as_view(), name='contact_us'),
]
