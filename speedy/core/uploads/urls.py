from django.conf.urls import url

from . import views

app_name = 'speedy.core.uploads'
urlpatterns = [
    url(r'^upload/$', views.UploadView.as_view(), name='upload'),
]
