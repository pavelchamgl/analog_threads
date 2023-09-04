from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission

from users.models import User, Follow


class NotAuthenticate(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return True


class PublicOrPrivateProfilePermission(BasePermission):
    def has_permission(self, request, view):
        profile_id = None
        followee_id = view.kwargs.get('followee_pk')
        follower_id = view.kwargs.get('follower_pk')
        profile_id = followee_id or follower_id
        if profile_id is None:
            return False
        profile = get_object_or_404(User, pk=profile_id)
        if not profile.is_private:
            return True
        else:
            follow = Follow.objects.filter(
                followee_id=profile_id if followee_id else request.user.id,
                follower_id=request.user.id if followee_id else profile_id,
                allowed=True
            ).exists()
            return follow


class EmailVerified(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_email_verify:
            return True
