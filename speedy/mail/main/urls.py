from django.urls import path

from . import views

app_name = 'speedy.mail.main'
urlpatterns = [
    path(route='', view=views.MainPageView.as_view(), name='main_page'),
    path(route='<path:rest>', view=views.MainPageView.as_view(), name='main_page'),
]


