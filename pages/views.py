from django.db.models import Count, Q
from rest_framework import mixins, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.generics import (ListCreateAPIView,
                                     get_object_or_404)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import generics
from cloudinary.uploader import upload

from config.utils import ThreadsMainPaginatorLTE, ThreadsMainPaginatorInspector, ThreadsMainPaginator
from users.models import User
from users.permissions import EmailVerified
from . import serializers
from .base_views import BaseSearchView
from .models import Post, Comment, HashTag
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
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):
    """
    API view for user post model instances (List/Create/Destroy).
    """
    serializer_class = PostViewSerializer
    permission_classes = (IsAuthenticated, EmailVerified)
    pagination_class = ThreadsMainPaginator
    pagination_inspector = ThreadsMainPaginatorInspector

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

        serializer = PostCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Post added successfully.'},
                        status=status.HTTP_201_CREATED)

    @swagger_auto_schema(pagination_class=pagination_class, paginator_inspectors=[pagination_inspector])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PostDetailAPIView(APIView):
    """
    API view for view detail post model instance.
    """
    permission_classes = (IsAuthenticated, EmailVerified)

    def get(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            serializer = PostViewSerializer(post, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)


class RepostCreateAPIVIew(APIView):
    permission_classes = (IsAuthenticated, EmailVerified)

    @swagger_auto_schema(
        operation_description="This endpoint for repost.",
        responses={
            201: 'Repost added successfully.',
            404: 'Post not found.'
        }
    )
    def post(self, request, *args, **kwargs):
        post_id = self.kwargs['post_id']
        request.data['repost'] = post_id

        try:
            post = get_object_or_404(Post, id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RepostCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Repost added successfully.'}, status=status.HTTP_201_CREATED)


class QuoteCreateAPIVIew(APIView):
    permission_classes = (IsAuthenticated, EmailVerified)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['text'],
        ),
        responses={
            201: 'Quote added successfully.',
            404: 'Post not found.'
        }
    )
    def post(self, request, *args, **kwargs):
        post_id = self.kwargs['post_id']
        request.data['repost'] = post_id

        try:
            post = get_object_or_404(Post, id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuoteCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Quote added successfully.'}, status=status.HTTP_201_CREATED)


class PostLikeUnlikeAPIView(APIView):
    permission_classes = (IsAuthenticated, EmailVerified)

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
    API endpoint for view post comments.
    """
    serializer_class = CommentViewSerializer
    permission_classes = (IsAuthenticated, EmailVerified)
    pagination_class = ThreadsMainPaginator
    pagination_inspector = ThreadsMainPaginatorInspector

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method == 'POST':
            return [CommentPermission()]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, pk=post_id)
        queryset = Comment.objects.filter(post=post).order_by('-date_posted')
        return queryset

    @swagger_auto_schema(
        operation_description="API endpoint for add post comment.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['text'],
        ),
        responses={
            201: 'Comment added successfully.',
            404: 'Post not found.'
        }
    )
    def post(self, request, *args, **kwargs):
        post_id = self.kwargs['post_id']
        request.data['post'] = post_id
        try:
            post = get_object_or_404(Post, id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'message': 'Comment added successfully.'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(pagination_class=pagination_class, paginator_inspectors=[pagination_inspector])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CommentDeleteAPIView(APIView):
    """
    This endpoint for comment delete.
    """
    permission_classes = (IsAuthenticated, EmailVerified)

    def delete(self, request, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)
        if comment.author != request.user:
            return Response({'error': 'You cannot delete this comment.'}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response({'message': 'Comment delete successfully.'}, status=status.HTTP_204_NO_CONTENT)


class ReplyCreateAPIView(APIView):
    """
    This endpoint for reply.
    """
    permission_classes = (IsAuthenticated, EmailVerified, ReplyPermission)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['text'],
        ),
        responses={
            201: 'Reply added successfully.',
            404: 'Comment not found.'
        }
    )
    def post(self, request, *args, **kwargs):
        comment_id = self.kwargs['comment_id']

        try:
            comment = get_object_or_404(Comment, id=comment_id)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)
        request.data['post'] = comment.post.id
        request.data['reply'] = comment.id
        serializer = ReplyCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Reply added successfully.'}, status=status.HTTP_201_CREATED)


class PostsByHashTagView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, EmailVerified)
    model = HashTag
    serializer_class = PostViewSerializer
    pagination_class = ThreadsMainPaginatorLTE
    pagination_inspector = ThreadsMainPaginatorInspector

    def get_queryset(self):
        tag_name = self.kwargs.get('tag_name')
        hashtag = get_object_or_404(HashTag, tag_name=tag_name)
        queryset = Post.objects.filter(hash_tag=hashtag).order_by('-pk', '-date_posted')
        return queryset

    @swagger_auto_schema(pagination_class=pagination_class, paginator_inspectors=[pagination_inspector])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ForYouFeedView(generics.ListAPIView):
    """For You feed page records"""
    permission_classes = (IsAuthenticated, EmailVerified)
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
    """
    Following feed page records
    """
    permission_classes = (IsAuthenticated, EmailVerified)
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


class UsersSearchView(BaseSearchView):
    """
    Search view for users by username
    """
    permission_classes = (IsAuthenticated, EmailVerified)
    model = User
    serializer_class = serializers.UserSearchSerializer

    def get_queryset(self):
        search_obj = self.kwargs.get('search_obj')
        queryset = User.objects.filter(username__icontains=search_obj)
        return queryset


class HashTagsSearch(BaseSearchView):
    """
    Search view for hashtags
    """
    permission_classes = (IsAuthenticated, EmailVerified)
    model = HashTag
    serializer_class = serializers.HashTagSearchSerializer

    def get_queryset(self):
        search_obj = self.kwargs.get('search_obj')
        queryset = HashTag.objects.filter(tag_name__icontains=search_obj)
        return queryset

