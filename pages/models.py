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
    text = models.CharField(max_length=1024, blank=True, null=True)
    # image = models.ImageField(upload_to="")
    date_posted = models.DateTimeField(auto_now_add=True)
    repost = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)
    comments_permission = models.CharField(max_length=20, choices=comments_permissions_type)
    mentioned_users = models.ManyToManyField(User, related_name='mentioned_in_posts', blank=True)
    likes = models.ManyToManyField(User, related_name='liked_post', blank=True)

    def total_likes(self):
        return self.likes.count()

    def user_like(self, user):
        return self.likes.filter(pk=user.pk).exists()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        mentioned_usernames = re.findall(r'@(\w+)', self.text)
        mentioned_users = User.objects.filter(username__in=mentioned_usernames)
        self.mentioned_users.set(mentioned_users)


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

# class Notification(models.Model):
#     pass
