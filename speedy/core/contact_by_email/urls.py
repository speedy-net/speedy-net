"""
URL configuration for the contact by email app of Speedy Core.
"""
from django.urls import path

from . import views

app_name = 'speedy.core.contact_by_email'
urlpatterns = [
    path(route='', view=views.ContactUsView.as_view(), name='contact_us'),
]


