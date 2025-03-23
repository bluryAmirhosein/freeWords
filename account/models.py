from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Custom user model that extends the default Django user model.
    Adds custom fields for full name, email, and username.
    """
    full_name = models.CharField(max_length=255, null=True, blank=True, default="")
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.username


class ProfileUser(models.Model):
    """
    Profile model for the CustomUser.
    Contains additional information such as profile photo and bio.
    """
    user = models.ForeignKey(CustomUser, models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='blog/profile image/', blank=True, null=True, verbose_name='photo')
    bio = models.TextField(max_length=500, blank=True, null=True, default='')
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username