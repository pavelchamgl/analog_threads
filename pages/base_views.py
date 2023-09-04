from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from config.utils import ThreadsMainPaginator, ThreadsMainPaginatorInspector


class BaseSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    model = None
    serializer_class = None
    pagination_class = ThreadsMainPaginator
    pagination_inspector = ThreadsMainPaginatorInspector

    @swagger_auto_schema(pagination_class=pagination_class, paginator_inspectors=[pagination_inspector])
    def get(self, request, search_obj, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = ThreadsMainPaginator()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(result_page, many=True, context=self.get_serializer_context())
        return paginator.get_paginated_response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

