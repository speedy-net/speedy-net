from django.urls import re_path, include

from speedy.core.urls import app_name, urlpatterns

urlpatterns += [
    re_path(route=r'^contact/', view=include('speedy.core.contact_by_email.urls', namespace='contact')),
]


