from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('post-detail/<int:pk>/<slug:slug>/', views.BlogPostDetailView.as_view(), name='post-detail'),
    path('comment/delete/<int:comment_id>/', views.DeleteCommentView.as_view(), name='delete-comment'),
    path('comment/reply/<int:post_id>/<int:comment_id>/', views.ReplyCommentView.as_view(), name='reply-comment'),
    path('reply/<int:reply_id>/delete/', views.DeleteReplyView.as_view(), name='delete-reply'),
    path('post/<int:pk>/<slug:slug>/like/', views.LikePostView.as_view(), name='like-post'),
    path('post-creation/', views.PostCreationView.as_view(), name='post-creation'),
    path('post-creation/<int:pk>/', views.PostCreationView.as_view(), name='post-creation'),
    path('posts/', views.PostsShowView.as_view(), name='posts'),
    path('posts/delete/<int:pk>/', views.DeletePostView.as_view(), name='delete'),
]
