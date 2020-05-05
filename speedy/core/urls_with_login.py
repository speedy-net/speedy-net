from django.urls import re_path, include

from speedy.core.urls import app_name, urlpatterns

urlpatterns += [
    re_path(route=r'^privacy/', view=include('speedy.core.privacy.urls', namespace='privacy')),
    re_path(route=r'^terms/', view=include('speedy.core.terms.urls', namespace='terms')),
    re_path(route=r'^contact/', view=include('speedy.core.contact_by_form.urls', namespace='contact')),
]


