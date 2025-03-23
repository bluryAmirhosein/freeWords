from django.contrib import admin
from .models import BlogPost, Comment, Tag, PostLike
from image_cropping.admin import ImageCroppingMixin



# Registering the BlogPost model with the admin panel
@admin.register(BlogPost)
class BlogPostAdmin(ImageCroppingMixin, admin.ModelAdmin):
    """
    Admin configuration for the BlogPost model.

    This class customizes the admin panel for managing blog posts, including:
    - Displaying the title, creation date, and cover image in the list view
    - Enabling filtering by creation date
    - Adding search functionality by title and description
    - Automatically generating slugs from the title
    """

    # Fields to display in the blog post list in the admin panel
    list_display = ('title_heading', 'created_at', 'cover_image', )

    # Filters available in the admin panel (filtering by creation date)
    list_filter = ('created_at',)

    # Fields that can be searched in the admin panel (searching by title and description)
    search_fields = ('title_heading', 'title_description')

    # Automatically generate the slug based on the title_heading field
    prepopulated_fields = {'slug': ('title_heading',)}


# Registering the Comment model with the admin panel
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Comment model.

    This class customizes the admin panel for managing comments, including:
    - Displaying post title, user, and creation date in the list view
    - Enabling search functionality by post title, username, and comment content
    """

    # Fields to display in the comment list in the admin panel
    list_display = ('post', 'user', 'created_at')

    # Fields that can be searched in the admin panel (searching by post title, username, and content)
    search_fields = ('post__title', 'user__username', 'content')


# Registering the Tag model with the admin panel
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Tag model.

    This class customizes the admin panel for managing tags, including:
    - Displaying tag name and creation date in the list view
    - Enabling filtering by tag name
    """

    # Fields to display in the tag list in the admin panel
    list_display = ['name', 'created_at']

    # Filters available in the admin panel (filtering by tag name)
    list_filter = ['name']


# Registering the PostLike model with the admin panel
@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    """
    Admin configuration for the PostLike model.

    This class customizes the admin panel for managing post likes, including:
    - Displaying user and post information in the list view
    - Enabling filtering by post
    """

    # Fields to display in the post like list in the admin panel
    list_display = ['user', 'post']

    # Filters available in the admin panel (filtering by post)
    list_filter = ['post']

