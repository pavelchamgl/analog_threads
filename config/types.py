from pages.models import Post, Comment
from users.models import User


class NotificationType:
    @staticmethod
    def test():
        type_ = 'test'
        message = "All is work fine!"
        return Notification(type_, message)

    @staticmethod
    def new_thread():
        type_ = 'new_thread'
        message = "We have new updates from people you follow!"
        return Notification(type_, message)

    @staticmethod
    def new_subscriber(user: User):
        type_ = 'new_subscriber'
        message = f'@{user.username} just followed you!'
        return Notification(type_, message, related_user=user)

    @staticmethod
    def new_thread_like(user: User):
        type_ = 'new_like'
        message = f'@{user.username} just liked your thread!'
        return Notification(type_, message, related_user=user)

    @staticmethod
    def new_comment_like(user: User, comment: Comment):
        type_ = 'new_like'
        message = f'@{user.username} just liked your comment!'
        return Notification(type_, message, related_user=user, related_comment=comment)

    @staticmethod
    def new_comment(user: User, related_post: Post, comment: Comment):
        type_ = 'new_comment'
        message = f'@{user.username} just commented on your thread!'
        return Notification(type_, message, related_user=user, related_post=related_post, related_comment=comment)

    @staticmethod
    def new_mentions_in_comment(user: User, comment: Comment):
        type_ = 'new_mention'
        message = f'@{user.username} just mentioned you in a comment!'
        return Notification(type_, message, related_user=user, related_comment=comment)

    @staticmethod
    def new_mentions_in_thread(user: User, post: Post):
        type_ = 'new_mention'
        message = f'@{user.username} just mentioned you in a thread!'
        return Notification(type_, message, related_user=user, related_post=post)


class Notification:
    def __init__(self, type_, message, related_user=None, related_post=None, related_comment=None):
        self.type = type_
        self.message = message
        self.related_user = related_user
        self.related_post = related_post
        self.related_comment = related_comment
