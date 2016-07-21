from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.core.models import TimeStampedModel


class Feedback(TimeStampedModel):
    TYPE_FEEDBACK = 0
    TYPE_REPORT_ENTITY = 1
    TYPE_REPORT_FILE = 2
    TYPE_CHOICES = (
        (TYPE_FEEDBACK, _('Feedback')),
        (TYPE_REPORT_ENTITY, _('Abuse (User)')),
        (TYPE_REPORT_FILE, _('Abuse (Photo)')),
    )

    class Meta:
        verbose_name = _('feedback')
        verbose_name_plural = _('feedbacks')
        ordering = ('-date_created',)

    sender = models.ForeignKey(verbose_name=_('sender'), to=settings.AUTH_USER_MODEL,
                               on_delete=models.SET_NULL, null=True, blank=True)
    sender_name = models.CharField(verbose_name=_('your name'), max_length=255, blank=True)
    sender_email = models.EmailField(verbose_name=_('your email'), blank=True)
    type = models.PositiveIntegerField(verbose_name=_('type'))
    text = models.TextField(verbose_name=_('your message'))
    report_entity = models.ForeignKey(verbose_name=_('reported entity'), to='accounts.Entity',
                                      on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    report_file = models.ForeignKey(verbose_name=_('reported photo'), to='uploads.File',
                                    on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
