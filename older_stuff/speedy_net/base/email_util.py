from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from django.conf import settings


# TODO: check why google does not write the href to the link (prob. localhost/port)
def send_email_verification(to, url):
    context = {
        'url': url
    }

    subject = 'Please activate your email'
    text_body_template = get_template('base/email_verification.txt')
    # html_body_template = get_template('base/email_verification.html')

    text_body = text_body_template.render(context)
    # html_body = html_body_template.render(context)

    send_mail(subject, text_body, settings.DEFAULT_FROM_EMAIL, [to])


def send_password_reset(to, url):
    context = {
        'url': url
    }

    subject = 'Password reset link'
    text_body_template = get_template('base/password_reset_email.txt')
    # html_body_template = get_template('base/password_reset_email.html')


    text_body = text_body_template.render(context)
    # html_body = html_body_template.render(context)

    send_mail(subject, text_body, settings.DEFAULT_FROM_EMAIL, [to])
