from django.urls import path, include, re_path
from rest_framework import routers

<<<<<<< pages/urls.py
from pages import views

router = routers.DefaultRouter()
router.register('', views.PostModelViewSet, basename='post')


urlpatterns = [
    path('post/', include(router.urls)),
    re_path('post/like_unlike/(?P<post_id>.+)/', views.PostLikeUnlikeAPIView.as_view(), name='post_like_unlike'),
    re_path('post/(?P<post_id>.+)/comments/', views.CommentListCreateAPIView.as_view(), name='comment-list-create'),
    re_path('post/comments/(?P<comment_id>.+)/reply/', views.ReplyCreateAPIView.as_view(), name='reply'),
    re_path('post/(?P<post_id>.+)/repost/', views.RepostCreateAPIVIew.as_view(), name='repost_create'),
    re_path('post/(?P<post_id>.+)/quote/', views.QuoteCreateAPIVIew.as_view(), name='quote_create'),

    path('feed/for_you/', views.ForYouFeedView.as_view(), name='for_you_feed'),
    path('feed/following/', views.FollowingFeedView.as_view(), name='following_feed'),
]
