from django.conf.urls import url

from . import views

app_name = 'speedy.core.im'
urlpatterns = [
    url(regex=r'^compose/$', view=views.SendMessageToUserView.as_view(), name='user_send'),
]


