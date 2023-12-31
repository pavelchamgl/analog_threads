import re

from django.db import models

from users.models import User


class Post(models.Model):
    comments_permissions_type = [
        ('anyone', 'anyone'),
        ('your followers', 'your followers'),
        ('profiles you follow', 'profiles you follow'),
        ('mentioned only', 'mentioned only'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=280, blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    video = models.URLField(blank=True, null=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    repost = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)
    comments_permission = models.CharField(max_length=20, choices=comments_permissions_type)
    mentioned_users = models.ManyToManyField(User, related_name='mentioned_in_posts', blank=True)
    hash_tag = models.ManyToManyField("HashTag", related_name='hash_tag_in_posts', blank=True)
    likes = models.ManyToManyField(User, related_name='liked_post', blank=True)

    def total_likes(self):
        return self.likes.count()

    def user_like(self, user):
        return self.likes.filter(pk=user.pk).exists()

    def total_comments(self):
        return Comment.objects.filter(post=self).count()

    def add_hashtags(self, tag_list: list):
        for tag_name in tag_list:
            hashtag, created = HashTag.objects.get_or_create(tag_name=tag_name)
            self.hash_tag.add(hashtag)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.text:
            mentioned_usernames = re.findall(r'@(\w+)', self.text)
            mentioned_users = User.objects.filter(username__in=mentioned_usernames)
            self.mentioned_users.set(mentioned_users)

            hash_tag_list = re.findall(r'#(\w+)', self.text)
            self.add_hashtags(hash_tag_list)


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.CharField(max_length=1024)
    date_posted = models.DateTimeField(auto_now_add=True)
    reply = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_comment', blank=True)

    def total_likes(self):
        return self.likes.count()

    def user_like(self, user):
        return self.likes.filter(pk=user.pk).exists()


class HashTag(models.Model):
    tag_name = models.CharField(max_length=255, unique=True)


class Notification(models.Model):
    types = [
        ("test", "test"),
        ("new_thread", "new_thread"),
        ("new_repost", "new_repost"),
        ("new_quote", "new_quote"),
        ("new_subscriber", "new_subscriber"),
        ("subscribe_request", "subscribe_request"),
        ("unsubscribe_request", "unsubscribe_request"),
        ("follow", "follow"),
        ("unfollow", "unfollow"),
        ("subscribe_allowed", "subscribe_allowed"),
        ("unsubscribe_allowed", "unsubscribe_allowed"),
        ("new_like", "new_like"),
        ("new_dislike", "new_dislike"),
        ("new_comment", "new_comment"),
        ("new_mention", "new_mention"),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=1024)
    type = models.CharField(max_length=20, choices=types)
    related_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='related_user', blank=True, null=True)
    related_post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    related_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True)
    date_posted = models.DateTimeField(auto_now_add=True)
