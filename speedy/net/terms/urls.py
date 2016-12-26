from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'', views.TermsOfServiceView.as_view(), name='terms_of_service'),
]
