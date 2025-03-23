from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


@shared_task
def send_reset_email(subject, email, reset_link, username):
    """
    Celery task to send a password reset email to the user.

    This task is responsible for sending an email with a password reset link to the user.
    It renders the email content from an HTML template and sends it using the Django email backend.

    Args:
        subject (str): The subject of the email.
        email (str): The recipient's email address.
        reset_link (str): The URL to reset the user's password.
        username (str): The username of the user who requested the password reset.

    Sends:
        A password reset email to the provided email address.
    """

    # Render the email content using the 'password-reset-email.html' template
    message = render_to_string('account/password-reset-email.html', {
        'user': username,
        'reset_link': reset_link,
    })

    # Send the email to the specified recipient
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])