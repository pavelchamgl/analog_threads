from rest_framework.permissions import BasePermission


class NotAuthenticate(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return True


# TODO write permission
class PublicOrPrivateProfilePermission(BasePermission):
    def has_permission(self, request, view):
        return True
