from django.conf.urls import url

from . import views

app_name = 'speedy.core.about'
urlpatterns = [
    url(r'', views.AboutView.as_view(), name='about'),
]


