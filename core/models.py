from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse
from account.models import CustomUser
from image_cropping import ImageCropField, ImageRatioField
from PIL import Image


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title_heading = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    title_description = models.CharField(max_length=250)
    description = RichTextUploadingField(verbose_name='Description')
    cover_image = models.ImageField(upload_to='blog/cover_image/', blank=True, null=True, verbose_name='Cover Image')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')


    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = 'Blog Post'
        verbose_name_plural = 'BlogPosts'
        ordering = ['-created_at']

    def __str__(self):
        return self.title_heading

    def get_absolute_url(self):
        return reverse('core:post-detail', args=(self.id, self.slug))


class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    reply = models.ForeignKey('self', null=True, blank='True', on_delete=models.CASCADE, related_name='replies')
    is_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f'Comment by {self.user.full_name} on {self.post.title_heading}'

    def get_replies(self):
        return self.replies.all()


class PostLike(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']

    def __str__(self):
        return f'{self.user.username} like {self.post.title_heading}'
