import random

from django.core.mail import send_mail

from django.conf import settings


def send_reset_email(email, username):
    otp = random.randint(1000, 9999)

    subject = 'Reset Password Confirmation'
    message = f'Hi {username},\n\n There is you code to reset you password: {otp}'
    from_email = settings.EMAIL_HOST_USER  # Replace with a no-reply email addressr

    try:
        send_mail(subject, message, from_email, [email])
        success_message = 'Reset password email sent successfully!'
    except Exception as e:
        success_message = f'Error sending email: {str(e)}'

    return otp, success_message
