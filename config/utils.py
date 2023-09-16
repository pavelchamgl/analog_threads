from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import PaginatorInspector
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


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

