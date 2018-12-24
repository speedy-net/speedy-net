from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from speedy.core.base.mail import mail_managers
from speedy.core.base.models import TimeStampedModel


class Feedback(TimeStampedModel):
    TYPE_FEEDBACK = 0
    TYPE_REPORT_ENTITY = 1
    TYPE_REPORT_FILE = 2
    TYPE_CHOICES = (
        (TYPE_FEEDBACK, _('Feedback')),
        (TYPE_REPORT_ENTITY, _('Abuse (User)')),
        (TYPE_REPORT_FILE, _('Abuse (Photo)')),
    )

    sender = models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name=_('sender'), on_delete=models.SET_NULL, blank=True, null=True)
    sender_name = models.CharField(verbose_name=_('your name'), max_length=255, blank=True)
    sender_email = models.EmailField(verbose_name=_('your email'), blank=True)
    type = models.PositiveIntegerField(verbose_name=_('type'), choices=TYPE_CHOICES)
    text = models.TextField(verbose_name=_('your message'))
    report_entity = models.ForeignKey(to='accounts.Entity', verbose_name=_('reported entity'), on_delete=models.SET_NULL, blank=True, null=True, related_name='complaints')
    report_file = models.ForeignKey(to='uploads.File', verbose_name=_('reported photo'), on_delete=models.SET_NULL, blank=True, null=True, related_name='complaints')

    class Meta:
        verbose_name = _('feedback')
        verbose_name_plural = _('feedbacks')
        ordering = ('-date_created',)

    def __str__(self):
        if (self.type == self.TYPE_REPORT_ENTITY):
            on = ' on {}'.format(self.report_entity.user)
        elif (self.type == self.TYPE_REPORT_FILE):
            on = ' on {}'.format(self.report_file)
        else:
            on = ''
        if (self.sender):
            by = str(self.sender)
        else:
            by = self.sender_name
        return '{}{} by {}'.format(self.get_type_display(), on, by)


@receiver(models.signals.post_save, sender=Feedback)
def email_feedback(sender, instance: Feedback, created: bool, **kwargs):
    if (created):
        mail_managers(template_name_prefix='feedback/email/admin_feedback', context={'feedback': instance}, headers={'Reply-To': instance.sender_email or instance.sender.email})


