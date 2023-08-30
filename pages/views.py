from django.db.models import Count, Q
from rest_framework import mixins, status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import (ListCreateAPIView,
                                     get_object_or_404,
                                     CreateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import generics
from cloudinary.uploader import upload

from config.utils import ThreadsMainPaginatorLTE, ThreadsMainPaginatorInspector
from .models import Post, Comment
from .permissions import (CommentPermission,
                          ReplyPermission)
from .serializers import (PostViewSerializer,
                          PostCreateSerializer,
                          CommentCreateSerializer,
                          CommentViewSerializer,
                          RepostCreateSerializer,
                          QuoteCreateSerializer,
                          ReplyCreateSerializer)


class PostModelViewSet(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):
    """
    API view for user post model instances (List/Retrieve/Destroy).
    """
    serializer_class = PostViewSerializer
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
        request.data['author'] = user.id

        image = request.FILES.get('image')
        video = request.FILES.get('video')

        image_allowed_formats = ['image/png', 'image/jpeg', 'image/gif']
        image_max_file_size = {
            'image/png': 3 * 1024 * 1024,  # 3 MB
            'image/jpeg': 3 * 1024 * 1024,  # 3 MB
            'image/gif': 15 * 1024 * 1024,  # 15 MB
        }

        video_allowed_formats = ['video/mp4']
        video_max_file_size = {'video/mp4': 15 * 1024 * 1024}  # 15 MB

        if image and not video:
            if image.content_type not in image_allowed_formats:
                return Response({'message': 'Invalid image format. Only PNG, JPEG, and GIF formats are allowed.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if image.size > image_max_file_size.get(image.content_type, 0):
                return Response({'message': 'File size should be within PNG/JPG- 3 MB and GIF - 15 MB.'},
                                status=status.HTTP_400_BAD_REQUEST)

            image_response = upload(image,
                                    folder="image/",
                                    transformation=[
                                        {"width": "auto", "crop": "scale"},
                                        {'quality': "auto:best"},
                                        {'fetch_format': "auto"}
                                    ],
                                    resource_type='auto')
            request.data['image'] = image_response['secure_url']
        elif video and not image:
            if video.content_type not in video_allowed_formats:
                return Response({'message': 'Invalid video format. Only MP4 format are allowed.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if video.size > video_max_file_size.get(video.content_type, 0):
                return Response({'message': 'File size should be within MP4 - 15 MB.'},
                                status=status.HTTP_400_BAD_REQUEST)

            video_response = upload(video,
                                    folder="video/",
                                    transformation=[
                                        {"width": "auto", "crop": "scale"},
                                        {'quality': "auto:best"},
                                        {'fetch_format': "auto"}
                                    ],
                                    resource_type='auto')
            request.data['video'] = video_response['secure_url']
        elif image and video:
            return Response({'message': 'You can\'t provide both an image and a video. Choose one.'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = PostCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Post added successfully.'},
                        status=status.HTTP_201_CREATED)


class RepostCreateAPIVIew(CreateAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="This endpoint for repost.",
        responses={
            200: 'Repost added successfully.',
            404: 'Post not found.'
        }
    )
    def post(self, request, *args, **kwargs):
        user = self.request.user
        request.data['author'] = user.id
        post_id = self.kwargs['post_id']
        request.data['repost'] = post_id

        try:
            post = get_object_or_404(Post, id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RepostCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Repost added successfully.'}, status=status.HTTP_201_CREATED)


class QuoteCreateAPIVIew(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuoteCreateSerializer

    @swagger_auto_schema(
        operation_description="This endpoint for quote.",
        responses={
            200: 'Quote added successfully.',
            404: 'Post not found.'
        }
    )
    def post(self, request, *args, **kwargs):
        user = self.request.user
        request.data['author'] = user.id
        post_id = self.kwargs['post_id']
        request.data['repost'] = post_id

        try:
            post = get_object_or_404(Post, id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Quote added successfully.'}, status=status.HTTP_201_CREATED)


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
            return Response({'message': 'Like removed.'}, status=status.HTTP_200_OK)


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
        return Response({'message': 'Comment added successfully.'}, status=status.HTTP_201_CREATED)


class ReplyCreateAPIView(CreateAPIView):
    serializer_class = ReplyCreateSerializer
    permission_classes = [IsAuthenticated, ReplyPermission]

    @swagger_auto_schema(
        operation_description="This endpoint for reply.",
        responses={
            200: 'Reply added successfully.',
            404: 'Comment not found.'
        }
    )
    def post(self, request, *args, **kwargs):
        request.data['author'] = request.user.id
        comment_id = self.kwargs['comment_id']

        try:
            comment = get_object_or_404(Comment, id=comment_id)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)
        request.data['post'] = comment.post.id
        request.data['reply'] = comment.id
        serializer = ReplyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Reply added successfully.'}, status=status.HTTP_201_CREATED)


class ForYouFeedView(generics.ListAPIView):
    """For You feed page records"""
    permission_classes = [IsAuthenticated]
    model = Post
    serializer_class = PostViewSerializer
    pagination_class = ThreadsMainPaginatorLTE
    pagination_inspector = ThreadsMainPaginatorInspector

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = Post.objects.exclude(
            Q(author__followee__follower_id=user_id) | Q(author=user_id) | Q(author__is_private=True)
        ).annotate(likes_count=Count('likes')).order_by('-date_posted', '-pk', '-likes_count')
        return queryset

    @swagger_auto_schema(pagination_class=pagination_class, paginator_inspectors=[pagination_inspector])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class FollowingFeedView(generics.ListAPIView):
    """Following feed page records"""
    permission_classes = [IsAuthenticated]
    model = Post
    serializer_class = PostViewSerializer
    pagination_class = ThreadsMainPaginatorLTE
    pagination_inspector = ThreadsMainPaginatorInspector

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = Post.objects.filter(
            author__followee__follower_id=user_id, author__followee__allowed=True
        ).order_by('-date_posted', '-pk')
        return queryset

    @swagger_auto_schema(pagination_class=pagination_class, paginator_inspectors=[pagination_inspector])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
