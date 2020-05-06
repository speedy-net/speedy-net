from django.urls import path

from . import views

app_name = 'speedy.core.terms'
urlpatterns = [
    path(route='', view=views.TermsOfServiceView.as_view(), name='terms_of_service'),
    path(route='<path:rest>', view=views.TermsOfServiceView.as_view(), name='terms_of_service'),
]


