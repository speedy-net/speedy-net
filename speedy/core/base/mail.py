import logging
from collections import namedtuple

from django.conf import settings as django_settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import get_language, gettext_lazy as _

logger = logging.getLogger(__name__)

RenderedMail = namedtuple('RenderedMail', 'subject body_plain body_html')


def render_mail(template_name_prefix, context=None, base_template_name_prefix='email/base'):
    subject_template_name = '{}_subject.txt'.format(template_name_prefix)
    plain_template_name = '{}_body.txt'.format(template_name_prefix)
    html_template_name = '{}_body.html'.format(template_name_prefix)

    plain_base_template_name = '{}_body.txt'.format(base_template_name_prefix)
    html_base_template_name = '{}_body.html'.format(base_template_name_prefix)

    context = context or {}
    site = Site.objects.get_current()
    params = {
        'protocol': 'https' if (django_settings.USE_HTTPS) else 'http',
        'language_code': translation.get_language() or 'en',  # ~~~~ TODO: find solution in order find language in management commands (None is this case).
        'domain': site.domain,
    }
    context.update({
        'SITE_URL': '{protocol}://{language_code}.{domain}'.format(**params),
        'SITE_MAIN_URL': '{protocol}://www.{domain}'.format(**params),
    })

    # render subject
    subject = render_to_string(template_name=subject_template_name, context=context)

    # render plain text
    context.update({
        'subject': subject,
        'base_template': plain_base_template_name,
    })
    body_plain = render_to_string(template_name=plain_template_name, context=context)

    # render html
    context.update({
        'plain_content': body_plain,
        'base_template': html_base_template_name,
    })
    try:
        body_html = render_to_string(template_name=html_template_name, context=context)
    except TemplateDoesNotExist:
        body_html = render_to_string(template_name=html_base_template_name, context=context)

    return RenderedMail(
        subject=' '.join(subject.splitlines(keepends=False)).strip(),
        body_plain=body_plain.strip(),
        body_html=body_html.strip(),
    )


def send_mail(to, template_name_prefix, context=None, **kwargs):
    # Sending mail may fail. If it fails, log the error and continue.
    try:
        site = Site.objects.get_current()
        language_code = get_language()
        context = context or {}
        context.update({
            'site_name': _(site.name),
        })
        rendered = render_mail(template_name_prefix=template_name_prefix, context=context)
        logger.debug('send_mail::site={site}, to={to}, template_name_prefix={template_name_prefix}, subject="{subject}", language_code={language_code}.'.format(
            site=_(site.name),
            to=to,
            template_name_prefix=template_name_prefix,
            subject=rendered.subject,
            language_code=language_code,
        ))
        msg = EmailMultiAlternatives(
            subject=rendered.subject,
            body=rendered.body_plain,
            to=to,
            **kwargs
        )
        msg.attach_alternative(rendered.body_html, 'text/html')
        return msg.send()
    except Exception as e:
        logger.error('send_mail::to={to}, template_name_prefix={template_name_prefix}, Exception={e}'.format(
            to=to,
            template_name_prefix=template_name_prefix,
            e=str(e),
        ))


def mail_managers(template_name_prefix, context=None, **kwargs):
    return send_mail(to=[a[1] for a in django_settings.MANAGERS], template_name_prefix=template_name_prefix, context=context, **kwargs)


