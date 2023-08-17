from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Post, Comment


class RepostViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'author', 'text', 'repost', 'date_posted']


class PostViewSerializer(serializers.ModelSerializer):
    repost = RepostViewSerializer()
    total_likes = SerializerMethodField()
    user_like = SerializerMethodField()

    def get_total_likes(self, obj):
        return obj.total_likes()

    def get_user_like(self, obj):
        return obj.user_like(self.context['request'].user)

    class Meta:
        model = Post
        fields = ['id', 'author', 'text', 'date_posted', 'repost', 'comments_permission', 'total_likes', 'user_like']


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['author', 'text', 'comments_permission']


class RepostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['author', 'repost']


class QuoteCreateSerializer(serializers.ModelSerializer):
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
    text = serializers.CharField(required=True)

    class Meta:
        model = Comment
        fields = ['post', 'author', 'text']
