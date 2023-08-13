from rest_framework import serializers

from .models import Post


class RepostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['author', 'text', 'date_posted']


class PostSerializer(serializers.ModelSerializer):
    repost = RepostSerializer()

    class Meta:
        model = Post
        fields = ['author', 'text', 'date_posted', 'repost', 'comments_permission']


class PostCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ['author', 'text', 'date_posted', 'repost', 'comments_permission']

