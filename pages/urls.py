from django.urls import path, include, re_path
from rest_framework import routers

from .views import (PostModelViewSet,
                    PostLikeUnlikeAPIView,
                    CommentListCreateAPIView,
                    RepostCreateAPIVIew,
                    QuoteCreateAPIVIew,
                    ReplyCreateAPIView)


router = routers.DefaultRouter()
router.register('', PostModelViewSet, basename='post')


urlpatterns = [
    path('post/', include(router.urls)),
    re_path('post/like_unlike/(?P<post_id>.+)/', PostLikeUnlikeAPIView.as_view(), name='post_like_unlike'),
    re_path('post/(?P<post_id>.+)/comments/', CommentListCreateAPIView.as_view(), name='comment-list-create'),
    re_path('post/comments/(?P<comment_id>.+)/reply/', ReplyCreateAPIView.as_view(), name='reply'),
    re_path('post/(?P<post_id>.+)/repost/', RepostCreateAPIVIew.as_view(), name='repost_create'),
    re_path('post/(?P<post_id>.+)/quote/', QuoteCreateAPIVIew.as_view(), name='quote_create'),
]
