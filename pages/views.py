from rest_framework import mixins, status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListCreateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .models import Post, Comment
from .permissions import CommentPermission
from .serializers import PostSerializer, PostCreateSerializer, CommentCreateSerializer, CommentViewSerializer


class PostModelViewSet(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):
    """
    API view for user post model instances (List/Retrieve/Destroy).
    """
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

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
        request.data["author"] = user.id
        serializer = PostCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Post added successfully.'}, status=status.HTTP_201_CREATED)


class PostLikeUnlikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="This endpoint like/unlike post.",
        responses={
            200: 'Like added. / Like removed.',
            404: 'Post not found.'
        }
    )
    def patch(self, request, post_id):
        user = request.user

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not post.likes.filter(id=user.id).exists():
            post.likes.add(user.id)
            return Response({'message': 'Like added.'}, status=status.HTTP_200_OK)
        elif post.likes.filter(id=user.id).exists():
            post.likes.remove(user.id)
            return Response({'success': 'Like removed.'}, status=status.HTTP_200_OK)


class CommentListCreateAPIView(ListCreateAPIView):
    """
    API endpoint for comment model instances (List/Create).
    """
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CommentViewSerializer
        elif self.request.method == 'POST':
            return CommentCreateSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method == 'POST':
            return [CommentPermission()]

    def get_queryset(self):
        return Comment.objects.order_by('-date_posted')

    def create(self, request, *args, **kwargs):
        user = self.request.user
        request.data['author'] = user.id
        post_id = self.kwargs['post_id']
        request.data['post'] = post_id
        try:
            post = get_object_or_404(Post, id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'message': 'Post added successfully.'}, status=status.HTTP_201_CREATED)
