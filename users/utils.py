import random

from django.core.mail import send_mail

from django.conf import settings


def send_reset_email(email, username):
    """
    status code 1 - send successfully
    status code 0 - error sending message
    """
    otp = random.randint(1000, 9999)

    subject = 'Reset Password Confirmation'
    message = f'Hi {username},\n\n There is you code to reset you password: {otp}'
    from_email = settings.EMAIL_HOST_USER

    try:
        send_mail(subject, message, from_email, [email])
        success_message = 'Reset password email sent successfully!'
        status_code = 1
    except Exception as e:
        success_message = f'Error sending email: {str(e)}'
        status_code = 0
    return otp, status_code
