from django.db import models
from django.utils import timezone

from users.models import User


class Post(models.Model):
    text = models.CharField(max_length=1024, blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    repost = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)


class PostImage(models.Model):
    image = models.ImageField(upload_to="")
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Like(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Comments(models.Model):
    text = models.CharField(max_length=1024)
    date_posted = models.DateTimeField(default=timezone.now)
    reply = models.ForeignKey("self", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

# class Notification(models.Model):
#     pass
