from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        if not username:
            raise ValueError("The Username field must be set.")
        email = self.normalize_email(email)
        username = username.lower()
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=32, unique=True)
    full_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    photo = models.URLField(blank=True, null=True)
    bio = models.CharField(max_length=254, blank=True, null=True)
    website = models.URLField(max_length=124, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    is_email_verify = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователи"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Follow(models.Model):
    followee = models.ForeignKey(User, related_name='followee', on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name='follower', on_delete=models.CASCADE)
    allowed = models.BooleanField(default=True)


class OTP(models.Model):
    title = models.CharField(max_length=128)
    value = models.IntegerField(blank=True, null=True)
    expired_date = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
