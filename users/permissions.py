from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission

from users.models import User, Follow


class NotAuthenticate(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return True


# TODO write permission
class PublicOrPrivateProfilePermission(BasePermission):
    def has_permission(self, request, view):
        followee_id = view.kwargs.get('followee_pk')
        print(followee_id)
        followee = get_object_or_404(User, pk=followee_id)
        if not followee.is_private:
            return True
        else:
            follow = Follow.objects.filter(followee_id=followee_id, follower_id=request.user.id, allowed=True).exists()
            return follow
