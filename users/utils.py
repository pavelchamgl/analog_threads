import random

from django.conf import settings
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from users.models import OTP, User


def otp_update_or_create(otp_title, otp_value, email):
    try:
        otp = OTP.objects.get(user__email=email, title=otp_title)
        otp.value = otp_value
    except OTP.DoesNotExist:
        user = User.objects.get(email=email)
        otp = OTP(user=user, title=otp_title, value=otp_value, expired_date=timezone.now() + settings.OTP_LIFETIME)
    otp.save()


def send_email(email, subject, message, username=None, otp=None):
    """
    status code 1 - send successfully
    status code 0 - error sending message
    """

    if '{username}' in message:
        message = message.replace('{username}', username)

    if '{email}' in message:
        message = message.replace('{email}', email)

    if '{otp}' in message:
        message = message.replace('{otp}', str(otp))

    from_email = settings.EMAIL_HOST_USER

    try:
        send_mail(subject, message, from_email, [email])
        status_code = 1
    except Exception as e:
        status_code = 0
    return status_code
