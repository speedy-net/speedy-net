from collections import namedtuple

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string

RenderedMail = namedtuple('RenderedMail', 'subject body_plain body_html')


def render_mail(template_name_prefix, context=None, base_template_name_prefix='email/base'):
    subject_template_name = '{}_subject.txt'.format(template_name_prefix)
    plain_template_name = '{}_body.txt'.format(template_name_prefix)
    html_template_name = '{}_body.html'.format(template_name_prefix)

    plain_base_template_name = '{}_body.txt'.format(base_template_name_prefix)
    html_base_template_name = '{}_body.html'.format(base_template_name_prefix)

    context = context or {}
    context.update({
        'SITE_URL': settings.SITE_URL,
        'SITE_NAME': settings.SITE_NAME,
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
