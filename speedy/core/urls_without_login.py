from django.urls import path, include

import speedy.core.base.path_converters
from speedy.core.urls import app_name, urlpatterns

urlpatterns += [
    path(route='contact/', view=include('speedy.core.contact_by_email.urls', namespace='contact')),
]


