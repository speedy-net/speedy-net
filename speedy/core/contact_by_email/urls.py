from django.urls import path

import speedy.core.base.path_converters
from . import views

app_name = 'speedy.core.contact_by_email'
urlpatterns = [
    path(route='', view=views.ContactUsView.as_view(), name='contact_us'),
]
