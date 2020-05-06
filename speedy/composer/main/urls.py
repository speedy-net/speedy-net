from django.urls import path

import speedy.core.base.path_converters
from . import views

app_name = 'speedy.composer.main'
urlpatterns = [
    path(route='', view=views.MainPageView.as_view(), name='main_page'),
    path(route='<path:rest>', view=views.MainPageView.as_view(), name='main_page'),
]


