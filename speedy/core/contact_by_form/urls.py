from django.urls import path

from . import views
from .models import Feedback

app_name = 'speedy.core.contact_by_form'
urlpatterns = [
    path(route='report/entity/<slug:report_entity_slug>/', view=views.FeedbackView.as_view(), kwargs={'type': Feedback.TYPE_REPORT_ENTITY}, name='report_entity'),
    path(route='report/file/<digits:report_file_id>/', view=views.FeedbackView.as_view(), kwargs={'type': Feedback.TYPE_REPORT_FILE}, name='report_file'),
    path(route='thank-you/', view=views.FeedbackSuccessView.as_view(), name='success'),
    path(route='', view=views.FeedbackView.as_view(), name='contact_us'),
]


