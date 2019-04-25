from django.conf.urls import url

from . import views

app_name = 'speedy.composer.main'
urlpatterns = [
    url(regex=r'', view=views.MainPageView.as_view(), name='main_page'),
]


