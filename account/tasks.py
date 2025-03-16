from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


@shared_task
def send_reset_email(subject, email, reset_link, username):
    message = render_to_string('account/password-reset-email.html', {
        'user': username,
        'reset_link': reset_link,
    })
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])