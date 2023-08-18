from rest_framework.permissions import BasePermission

from .models import Post, Comment


class CommentPermission(BasePermission):
    def has_permission(self, request, view):
        post_id = view.kwargs.get('post_id')
        post = Post.objects.get(id=post_id)
        if post.comments_permission == 'anyone':
            return True
        elif post.comments_permission == 'your followers':
            return post.author.follower.filter(followee=request.user).exists()
        elif post.comments_permission == 'profiles you follow':
            return post.author.followee.filter(follower=request.user).exists()
        elif post.comments_permission == 'mentioned only':
            return post.mentioned_users.filter(id=request.user.id).exists()
        return False


class ReplyPermission(BasePermission):
    def has_permission(self, request, view):
        comment_id = view.kwargs.get('comment_id')
        comment = Comment.objects.get(id=comment_id)
        post = Post.objects.get(id=comment.post.id)
        if post.comments_permission == 'anyone':
            return True
        elif post.comments_permission == 'your followers':
            return post.author.follower.filter(followee=request.user).exists()
        elif post.comments_permission == 'profiles you follow':
            return post.author.followee.filter(follower=request.user).exists()
        elif post.comments_permission == 'mentioned only':
            return post.mentioned_users.filter(id=request.user.id).exists()
        return False
