from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from users.models import User, Follow
from .models import Post, Comment, HashTag, Notification


class RepostViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'author', 'text', 'image', 'video', 'repost', 'date_posted']


class PostViewSerializer(serializers.ModelSerializer):
    repost = RepostViewSerializer()
    total_likes = SerializerMethodField()
    user_like = SerializerMethodField()
    total_comments = SerializerMethodField()

    def get_total_likes(self, obj):
        return obj.total_likes()

    def get_user_like(self, obj):
        return obj.user_like(self.context['request'].user)

    def total_comments(self, obj):
        return obj.total_comments()

    class Meta:
        model = Post
        fields = ['id', 'author', 'text', 'date_posted', 'image', 'video', 'repost', 'comments_permission',
                  'total_comments', 'total_likes', 'user_like']


class PostCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault(), write_only=True)

    class Meta:
        model = Post
        fields = ['author', 'text', 'image', 'video', 'comments_permission']


class RepostCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault(), write_only=True)

    class Meta:
        model = Post
        fields = ['author', 'repost']


class QuoteCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault(), write_only=True)
    text = serializers.CharField(required=True)

    class Meta:
        model = Post
        fields = ['author', 'text', 'repost']


class ReplyViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'author', 'text', 'date_posted']


class CommentViewSerializer(serializers.ModelSerializer):
    reply = ReplyViewSerializer()
    total_likes = SerializerMethodField()
    user_like = SerializerMethodField()

    def get_total_likes(self, obj):
        return obj.total_likes()

    def get_user_like(self, obj):
        return obj.user_like(self.context['request'].user)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'text', 'date_posted', 'reply', 'total_likes', 'user_like']


class CommentCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault(), write_only=True)
    text = serializers.CharField(required=True)

    class Meta:
        model = Comment
        fields = ['post', 'author', 'text']


class ReplyCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault(), write_only=True)
    text = serializers.CharField(required=True)

    class Meta:
        model = Comment
        fields = ['post', 'author', 'text', 'reply']


class UserSearchSerializer(serializers.ModelSerializer):
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['pk', 'username', 'is_followed']

    def get_is_followed(self, obj):
        user_id = self.context['request'].user.id
        followee_id = obj.id

        if user_id == followee_id:
            return "You"
        try:
            follow = Follow.objects.get(followee_id=followee_id, follower_id=user_id)
        except Follow.DoesNotExist:
            return "Not Followed"
        return "Followed" if follow.allowed else "Pending"


class HashTagSearchSerializer(serializers.ModelSerializer):
    posts_counts = serializers.SerializerMethodField()

    class Meta:
        model = HashTag
        fields = ['pk', 'tag_name', 'posts_counts']

    def get_posts_counts(self, obj):
        return obj.hash_tag_in_posts.all().count()


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["pk", "owner", "text", "related_user", "related_post", "related_comment", "date_posted"]
