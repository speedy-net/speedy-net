from django.urls import path

import speedy.core.base.path_converters
from . import views

app_name = 'speedy.core.about'
urlpatterns = [
    path(route='', view=views.AboutView.as_view(), name='about'),
    path(route='<path:rest>', view=views.AboutView.as_view(), name='about'),
]


