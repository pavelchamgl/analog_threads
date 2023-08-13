from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Post


class RepostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'author', 'text', 'date_posted']


class PostSerializer(serializers.ModelSerializer):
    repost = RepostSerializer()
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
        fields = ['author', 'text', 'date_posted', 'repost', 'comments_permission']

