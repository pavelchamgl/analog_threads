from django.urls import path, include, re_path
from rest_framework import routers

from pages import views


router = routers.DefaultRouter()
router.register('', views.PostModelViewSet, basename='post')


urlpatterns = [
    path('post/', include(router.urls)),
    re_path('post/like_unlike/(?P<post_id>.+)/', views.PostLikeUnlikeAPIView.as_view(), name='post_like_unlike'),
    re_path('post/(?P<post_id>.+)/comments/', views.CommentListCreateAPIView.as_view(), name='comment-list-create'),

    path('feed/for_you/', views.ForYouFeedView.as_view(), name='for_you_feed'),
    path('feed/following/', views.FollowingFeedView.as_view(), name='following_feed'),
]
