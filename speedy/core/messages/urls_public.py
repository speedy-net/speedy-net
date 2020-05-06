from django.urls import path

import speedy.core.base.path_converters
from . import views

app_name = 'speedy.core.messages'
urlpatterns = [
    path(route='compose/', view=views.SendMessageToUserView.as_view(), name='user_send'),
]


