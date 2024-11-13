from django.urls import path, include

from speedy.core.urls import app_name, urlpatterns

urlpatterns += [
    path(route='contact/', view=include(arg='speedy.core.contact_by_email.urls', namespace='contact')),
]


