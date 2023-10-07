from pages.models import Post, Comment
from users.models import User


class NotificationType:
    @staticmethod
    def test():
        return {
            "type": "test",
            "message": "All is work fine!",
            "related_user": None,
            "related_post": None,
            "related_comment": None,
        }
    # TODO

    @staticmethod
    def new_thread():
        return {
            "type": "new_thread",
            "message": "We have new updates from people you follow!",
            "related_user": None,
            "related_post": None,
            "related_comment": None,
        }

    @staticmethod
    def new_repost(user, post):
        return {
            "type": "new_repost",
            "message": f'@{user.username} just reposted your thread!',
            "related_user": user.id,
            "related_post": post.id,
            "related_comment": None,
        }
        # TODO

    @staticmethod
    def new_quote(user, post):
        return {
            "type": "new_repost",
            "message": f'@{user.username} just quoted your thread!',
            "related_user": user.id,
            "related_post": post.id,
            "related_comment": None,
        }
        # TODO

    @staticmethod
    def new_subscriber(user):
        return {
            "type": "new_subscriber",
            "message": f'@{user.username} just followed you!',
            "related_user": user.id,
            "related_post": None,
            "related_comment": None,
        }
        # TODO
    @staticmethod
    def subscribe_request(user):
        return {
            "type": "subscribe_request",
            "message": f'@{user.username} want to subscribe you!',
            "related_user": user.id,
            "related_post": None,
            "related_comment": None,
        }
        # TODO
    @staticmethod
    def subscribe_allowed(user):
        return {
            "type": "subscribe_allowed",
            "message": f'@{user.username} allow your subscribe request!',
            "related_user": user.id,
            "related_post": None,
            "related_comment": None,
        }
        # TODO

    @staticmethod
    def new_thread_like(user, post):
        return {
            "type": "new_like",
            "message": f'@{user.username} just liked your thread!',
            "related_user": user.id,
            "related_post": post.id,
            "related_comment": None,
        }

    @staticmethod
    def new_comment_like(user, comment):
        return {
            "type": "new_like",
            "message": f'@{user.username} just liked your comment!',
            "related_user": user.id,
            "related_post": None,
            "related_comment": comment.id,
        }

    @staticmethod
    def new_comment(user, related_post, comment):
        return {
            "type": "new_comment",
            "message": f'@{user.username} just commented on your thread!',
            "related_user": user.id,
            "related_post": related_post.id,
            "related_comment": comment.id,
        }

    @staticmethod
    def new_mentions_in_comment(user, comment):
        return {
            "type": "new_mention",
            "message": f'@{user.username} just mentioned you in a comment!',
            "related_user": user.id,
            "related_post": None,
            "related_comment": comment.id,
        }

    @staticmethod
    def new_mentions_in_thread(user, post):
        return {
            "type": "new_mention",
            "message": f'@{user.username} just mentioned you in a thread!',
            "related_user": user.id,
            "related_post": post.id,
            "related_comment": None,
        }

    @staticmethod
    def new_reply(user, comment):
        return {
            "type": "new_reply",
            "message": f'@{user.username} just replied to your comment!',
            "related_user": user.id,
            "related_post": None,
            "related_comment": comment.id,
        }