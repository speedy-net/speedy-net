from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'', views.MainPageView.as_view(), name='main_page'),
]
