from collections import namedtuple

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils import translation

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
        'protocol': 'https' if settings.USE_SSL else 'http',
        'language': translation.get_language() or 'en', # TODO find solution in order find language in management commands (None is this case)
        'domain': site.domain,
    }
    context.update({
        'SITE_URL': '{protocol}://{language}.{domain}'.format(**params),
        'SITE_MAIN_URL': '{protocol}://www.{domain}'.format(**params),
        'SITE_NAME': site.name,
    })

    # render subject
    subject = render_to_string(subject_template_name, context)

    # render plain text
    context.update({
        'subject': subject,
        'base_template': plain_base_template_name,
    })
    body_plain = render_to_string(plain_template_name, context)

    # render html
    context.update({
        'plain_content': body_plain,
        'base_template': html_base_template_name,
    })
    try:
        body_html = render_to_string(html_template_name, context)
    except TemplateDoesNotExist:
        body_html = render_to_string(html_base_template_name, context)

    return RenderedMail(
        subject=' '.join(subject.splitlines(keepends=False)).strip(),
        body_plain=body_plain.strip(),
        body_html=body_html.strip(),
    )


def send_mail(to, template_name_prefix, context=None, **kwargs):
    rendered = render_mail(template_name_prefix, context)
    msg = EmailMultiAlternatives(
        subject=rendered.subject,
        body=rendered.body_plain,
        to=to,
        **kwargs
    )
    msg.attach_alternative(rendered.body_html, 'text/html')
    return msg.send()


def mail_managers(template_name_prefix, context=None, **kwargs):
    return send_mail([a[1] for a in settings.MANAGERS], template_name_prefix, context, **kwargs)
