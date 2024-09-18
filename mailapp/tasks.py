from celery import shared_task
from django.core.mail import send_mail
from .models import RecipientEmail
from django.utils import timezone
from django.conf import settings


@shared_task(name="Send Mail")
def send_email_task(subject, body):
    recipients = RecipientEmail.objects.values_list("email", flat=True)
    send_mail(subject, body, settings.EMAIL_HOST_USER, recipients)


@shared_task(name="Send Mail Later")
def send_mail_later(subject, body, delay_time):
    print(delay_time)
    eta_time = timezone.now() + timezone.timedelta(seconds=0)
    send_email_task.apply_async(
        args=[subject, body],
        eta=eta_time,
    )
