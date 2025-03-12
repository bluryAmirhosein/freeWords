from django.contrib import admin
from .models import BlogPost, Comment, Tag, PostLike
from image_cropping.admin import ImageCroppingMixin


# @admin.register(BlogPost)
class BlogPostAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ('title_heading', 'created_at', 'cover_image', )
    list_filter = ('created_at',)
    search_fields = ('title_heading', 'title_description')
    prepopulated_fields = {'slug': ('title_heading',)}


admin.site.register(BlogPost, BlogPostAdmin)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    search_fields = ('post__title', 'user__username', 'content')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    list_filter = ['name']


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post']
    list_filter = ['post']