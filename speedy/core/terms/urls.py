from django.urls import path

import speedy.core.base.path_converters
from . import views

app_name = 'speedy.core.terms'
urlpatterns = [
    path(route='', view=views.TermsOfServiceView.as_view(), name='terms_of_service'),
    path(route='<path:rest>', view=views.TermsOfServiceView.as_view(), name='terms_of_service'),
]


