from collections import OrderedDict

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from drf_yasg import openapi
from drf_yasg.inspectors import PaginatorInspector
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from config import types
from config.types import NotificationType
from pages.models import Notification
from users.models import User


class ThreadsMainPaginatorInspector(PaginatorInspector):
    def get_paginator_parameters(self, paginator):
        return [
            openapi.Parameter(
                name='page_size',
                in_=openapi.IN_QUERY,
                description='Number of items per page',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                name='selected_id',
                in_=openapi.IN_QUERY,
                description='Filter items with an ID greater than or equal to this value',
                type=openapi.TYPE_INTEGER
            )
        ]

    def get_paginated_response(self, paginator, response_schema):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=OrderedDict((
                ('links', openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties=OrderedDict((
                        ('next', openapi.Schema(type=openapi.TYPE_INTEGER)),
                        ('previous', openapi.Schema(type=openapi.TYPE_INTEGER))
                    ))
                )),
                ('count', openapi.Schema(type=openapi.TYPE_INTEGER)),
                ('results', response_schema),
            )),
            required=['results'])


class ThreadsMainPaginator(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    selected_id = None
    selected_id_query_param = 'selected_id'
    lookup = 'id__gte'

    def paginate_queryset(self, queryset, request, view=None):
        selected_id = request.GET.get(self.selected_id_query_param) or self.selected_id

        if selected_id:
            try:
                selected_id = int(selected_id)
                lookup = {self.lookup: selected_id}
                queryset = queryset.filter(**lookup)
            except ValueError:
                pass

        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })


class ThreadsMainPaginatorLTE(ThreadsMainPaginator):
    lookup = 'id__lte'


def send_notification(recipient: User, notification_type: types.Notification):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        str(recipient.pk),
        {
            "type": "send_notification",
            "message": f'"{notification_type.type}": "{notification_type.message}"',
        },
    )
    Notification.objects.create(
        owner=recipient,
        text=notification_type.message,
        related_post=notification_type.related_post if notification_type.related_post else None,
        related_comment=notification_type.related_comment if notification_type.related_comment else None,
        related_user=notification_type.related_user if notification_type.related_user else None,
    )


def send_multiple_notification(users: User.objects, notification_type: types.Notification):
    for user in users:
        send_notification(user, notification_type)
