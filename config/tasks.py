from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.mail import send_mail

from config import types
from pages.models import Notification
from users.models import User


@shared_task
def send_notification(recipient_id: int, notification_data: dict, create_notification=True):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        str(recipient_id),
        {
            "type": "send_notification",
            "message": f'"{notification_data["type"]}": "{notification_data["message"]}"',
        },
    )
    if create_notification:
        Notification.objects.create(
            owner_id=recipient_id,
            text=notification_data["message"],
            type=notification_data['type'],
            related_post=notification_data.get("related_post"),
            related_comment=notification_data.get("related_comment"),
            related_user_id=notification_data.get("related_user"),
        )


@shared_task
def send_multiple_notifications(notification_type: dict, create_notification=True, **filters,):
    users = User.objects.filter(**filters)
    for user in users:
        send_notification(user.id, notification_type, create_notification=create_notification)


@shared_task
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
