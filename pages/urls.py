from django.urls import path, include, re_path
from rest_framework import routers

from .views import PostModelViewSet, PostLikeUnlikeAPIView


router = routers.DefaultRouter()
router.register('', PostModelViewSet, basename='post')


urlpatterns = [
    path('post/', include(router.urls)),
    re_path('post/like_unlike/(?P<post_id>.+)/', PostLikeUnlikeAPIView.as_view(), name='post_like_unlike'),
]
