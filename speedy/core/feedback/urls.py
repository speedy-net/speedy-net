from django.conf.urls import url

from . import views
from .models import Feedback

app_name = 'speedy.core.feedback'
urlpatterns = [
    url(regex=r'^report/entity/(?P<report_entity_slug>[-\w]+)/$', view=views.FeedbackView.as_view(), kwargs={'type': Feedback.TYPE_REPORT_ENTITY}, name='report_entity'),
    url(regex=r'^report/file/(?P<report_file_id>[-\w]+)/$', view=views.FeedbackView.as_view(), kwargs={'type': Feedback.TYPE_REPORT_FILE}, name='report_file'),
    url(regex=r'^thank-you/$', view=views.FeedbackSuccessView.as_view(), name='success'),
    url(regex=r'^$', view=views.FeedbackView.as_view(), name='feedback'),
]


