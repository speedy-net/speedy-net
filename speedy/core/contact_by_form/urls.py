from django.urls import re_path

from . import views
from .models import Feedback

app_name = 'speedy.core.contact_by_form'
urlpatterns = [
    re_path(route=r'^report/entity/(?P<report_entity_slug>[-\w]+)/$', view=views.FeedbackView.as_view(), kwargs={'type': Feedback.TYPE_REPORT_ENTITY}, name='report_entity'),
    re_path(route=r'^report/file/(?P<report_file_id>[-\w]+)/$', view=views.FeedbackView.as_view(), kwargs={'type': Feedback.TYPE_REPORT_FILE}, name='report_file'),
    re_path(route=r'^thank-you/$', view=views.FeedbackSuccessView.as_view(), name='success'),
    re_path(route=r'^$', view=views.FeedbackView.as_view(), name='contact_us'),
]


