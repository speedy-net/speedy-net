"""
URL configuration of Speedy Core for sites without login, extending the base Speedy Core URLs with the contact by email app.
"""
from django.urls import path, include

from speedy.core.urls import app_name, urlpatterns

urlpatterns += [
    path(route='contact/', view=include(arg='speedy.core.contact_by_email.urls', namespace='contact')),
]


