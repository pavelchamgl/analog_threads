from rest_framework import mixins, status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Post
from .serializers import PostSerializer, PostCreateSerializer


class PostModelViewSet(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):
    """
    API view for user post model instances (List/Retrieve/Destroy).
    """
    serializer_class = PostSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = Post.objects.filter(author=user_id).order_by("-date_posted")
        return queryset

    @swagger_auto_schema(
        request_body=PostCreateSerializer,
        operation_description="This endpoint creates new post.",
        responses={
            201: 'Post added successfully.',
            400: 'Bad Request'
        }
    )
    def create(self, request, *args, **kwargs):
        user = self.request.user
        request.data["user_id"] = user.id
        serializer = PostCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Post added successfully.'}, status=status.HTTP_201_CREATED)
