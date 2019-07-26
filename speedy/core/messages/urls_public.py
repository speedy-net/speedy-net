from django.conf.urls import url

from . import views

app_name = 'speedy.core.messages'
urlpatterns = [
    url(regex=r'^compose/$', view=views.SendMessageToUserView.as_view(), name='user_send'),
]


