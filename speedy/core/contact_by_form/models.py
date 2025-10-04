from django.conf import settings as django_settings
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator

from speedy.core.base.mail import mail_managers
from speedy.core.base.models import TimeStampedModel
from speedy.core.accounts.models import User


class Feedback(TimeStampedModel):
    """
    Represents feedback or reports submitted by users.

    Attributes:
        TYPE_FEEDBACK (int): Constant for feedback type.
        TYPE_REPORT_ENTITY (int): Constant for reporting an entity type.
        TYPE_REPORT_FILE (int): Constant for reporting a file type.
        TYPE_CHOICES (tuple): Choices for the type field.
        sender (ForeignKey): The user who sent the feedback.
        sender_name (CharField): The name of the sender.
        sender_email (EmailField): The email of the sender.
        type (SmallIntegerField): The type of feedback.
        text (TextField): The message content of the feedback.
        report_entity (ForeignKey): The reported entity (if applicable).
        report_file (ForeignKey): The reported file (if applicable).
    """
    TYPE_FEEDBACK = 0
    TYPE_REPORT_ENTITY = 1
    TYPE_REPORT_FILE = 2
    TYPE_CHOICES = (
        (TYPE_FEEDBACK, _('Feedback')),
        (TYPE_REPORT_ENTITY, _('Abuse (User)')),
        (TYPE_REPORT_FILE, _('Abuse (Photo)')),
    )

    sender: User = models.ForeignKey(to=django_settings.AUTH_USER_MODEL, verbose_name=_('sender'), on_delete=models.SET_NULL, blank=True, null=True, related_name='+')
    sender_name = models.CharField(verbose_name=_('your name'), max_length=255, blank=True)
    sender_email = models.EmailField(verbose_name=_('your email'), blank=True)
    type = models.SmallIntegerField(verbose_name=_('type'), choices=TYPE_CHOICES)
    text = models.TextField(verbose_name=_('your message'), max_length=50000, validators=[MaxLengthValidator(limit_value=50000)])
    if (True or django_settings.LOGIN_ENABLED):  # ~~~~ TODO: fix this model to work with sites without login.
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


@receiver(signal=models.signals.post_save, sender=Feedback)
def email_feedback(sender, instance: Feedback, created: bool, **kwargs):
    """
    Signal receiver that sends an email to managers when feedback is created.

    Args:
        sender (type): The model class that sent the signal.
        instance (Feedback): The instance of the Feedback model.
        created (bool): Whether the instance was created.
        **kwargs: Additional keyword arguments.
    """
    if (created):
        headers = {'Reply-To': instance.sender_email or instance.sender.email or "no-reply@{}".format(django_settings.DEFAULT_FROM_EMAIL.strip().rsplit("@", 1)[-1])}
        mail_managers(template_name_prefix='email/contact_by_form/admin_feedback', context={'feedback': instance}, headers=headers)


