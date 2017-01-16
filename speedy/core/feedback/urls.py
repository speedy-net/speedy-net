from django.conf.urls import url

from . import views
from .models import Feedback

urlpatterns = [
    url(r'^report/entity/(?P<report_entity_slug>[-\w]+)/$', views.FeedbackView.as_view(), kwargs={'type': Feedback.TYPE_REPORT_ENTITY}, name='report_entity'),
    url(r'^report/file/(?P<report_file_id>[-\w]+)/$', views.FeedbackView.as_view(), kwargs={'type': Feedback.TYPE_REPORT_FILE}, name='report_file'),
    url(r'^thank-you/$', views.FeedbackSuccessView.as_view(), name='success'),
    url(r'^$', views.FeedbackView.as_view(), name='feedback'),
]
