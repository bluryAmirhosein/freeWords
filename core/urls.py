from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Home URL: A view to display the home page of the site.
    # Name: 'home'
    # View: HomeView
    # This URL does not require any parameters.
    path('', views.HomeView.as_view(), name='home'),

    # Blog Post Detail URL: A view to display a detailed view of a specific blog post.
    # Name: 'post-detail'
    # View: BlogPostDetailView
    # Parameters:
    #   - pk: The primary key (ID) of the blog post
    #   - slug: A URL-friendly slug for the blog post
    path('post-detail/<int:pk>/<slug:slug>/', views.BlogPostDetailView.as_view(), name='post-detail'),

    # Delete Comment URL: A view for users to delete a comment they have made.
    # Name: 'delete-comment'
    # View: DeleteCommentView
    # Parameters:
    #   - comment_id: The unique ID of the comment to be deleted
    path('comment/delete/<int:comment_id>/', views.DeleteCommentView.as_view(), name='delete-comment'),

    # Reply to Comment URL: A view for users to reply to a specific comment on a blog post.
    # Name: 'reply-comment'
    # View: ReplyCommentView
    # Parameters:
    #   - post_id: The ID of the blog post
    #   - comment_id: The ID of the comment to reply to
    path('comment/reply/<int:post_id>/<int:comment_id>/', views.ReplyCommentView.as_view(), name='reply-comment'),

    # Delete Reply URL: A view for users to delete a reply to a comment.
    # Name: 'delete-reply'
    # View: DeleteReplyView
    # Parameters:
    #   - reply_id: The unique ID of the reply to be deleted
    path('reply/<int:reply_id>/delete/', views.DeleteReplyView.as_view(), name='delete-reply'),

    # Like Post URL: A view for users to like a specific blog post.
    # Name: 'like-post'
    # View: LikePostView
    # Parameters:
    #   - pk: The ID of the blog post to be liked
    #   - slug: The URL-friendly slug of the blog post
    path('post/<int:pk>/<slug:slug>/like/', views.LikePostView.as_view(), name='like-post'),

    # Post Creation URL: A view for users to create a new blog post.
    # Name: 'post-creation'
    # View: PostCreationView
    # This URL does not require any parameters.
    path('post-creation/', views.PostCreationView.as_view(), name='post-creation'),

    # Post Edit URL: A view to edit an existing blog post (based on its primary key).
    # Name: 'post-creation'
    # View: PostCreationView
    # Parameters:
    #   - pk: The ID of the blog post to be edited
    path('post-creation/<int:pk>/', views.PostCreationView.as_view(), name='post-creation'),

    # Posts List URL: A view to display a list of all blog posts.
    # Name: 'posts'
    # View: PostsShowView
    # This URL does not require any parameters.
    path('posts/', views.PostsShowView.as_view(), name='posts'),

    # Delete Post URL: A view to delete a specific blog post.
    # Name: 'delete'
    # View: DeletePostView
    # Parameters:
    #   - pk: The ID of the blog post to be deleted
    path('posts/delete/<int:pk>/', views.DeletePostView.as_view(), name='delete'),
]
