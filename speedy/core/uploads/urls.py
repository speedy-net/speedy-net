from django.conf.urls import url

from . import views

app_name = 'speedy.core.uploads'
urlpatterns = [
    url(regex=r'^upload/$', view=views.UploadView.as_view(), name='upload'),
]


