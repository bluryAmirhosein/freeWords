from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255, null=True, blank=True, default="")
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.username


class ProfileUser(models.Model):
    user = models.ForeignKey(CustomUser, models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='blog/profile image/', blank=True, null=True, verbose_name='photo')
    bio = models.TextField(max_length=500, blank=True, null=True, default='')
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.photo:
            img = Image.open(self.photo)
            img = img.convert("RGB")
            img = img.copy()
            img_io = BytesIO()
            img.save(img_io, format="WEBP", quality=50, optimize=True)

        self.photo = InMemoryUploadedFile(
            file=img_io,
            field_name=None,
            name=self.photo.name.split('.')[0] + ".webp",
            content_type="image/webp",
            size=img_io.tell(),
            charset=None
        )
        super().save(*args, **kwargs)