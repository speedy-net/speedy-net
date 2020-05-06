from django.urls import path

import speedy.core.base.path_converters
from . import views

app_name = 'speedy.match.profiles'
urlpatterns = [
    path(route='me/', view=views.MeView.as_view(), name='me'),
    path(route='me/<path:rest>', view=views.MeView.as_view(), name='me'),
    path(route='<slug:slug>/', view=views.UserDetailView.as_view(), name='user'),
]


