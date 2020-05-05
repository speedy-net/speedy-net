from django.urls import re_path

from . import views

app_name = 'speedy.core.about'
urlpatterns = [
    re_path(route=r'', view=views.AboutView.as_view(), name='about'),
]


