"""
URL configuration for the Speedy Core uploads app.
"""
from django.urls import path

from . import views

app_name = 'speedy.core.uploads'
urlpatterns = [
    path(route='upload/', view=views.UploadView.as_view(), name='upload'),
]


