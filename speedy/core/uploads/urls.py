from django.urls import re_path

from . import views

app_name = 'speedy.core.uploads'
urlpatterns = [
    re_path(route=r'^upload/$', view=views.UploadView.as_view(), name='upload'),
]


