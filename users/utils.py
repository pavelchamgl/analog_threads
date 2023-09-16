from django.conf import settings
from django.core.mail import send_mail
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
