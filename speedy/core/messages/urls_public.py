from django.urls import path

from . import views

app_name = 'speedy.core.messages'
urlpatterns = [
    path(route='compose/', view=views.SendMessageToUserView.as_view(), name='user_send'),
]


