from django import forms
from .models import Comment, BlogPost


class CommentForm(forms.ModelForm):
    """
    Form for users to submit a comment on a blog post.
    It includes a content field with a styled textarea widget.
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4,}),
        }


class ReplyForm(forms.ModelForm):
    """
    Form for users to reply to an existing comment.
    Similar to CommentForm but used specifically for replies.
    """
    class Meta:
        model = Comment
        fields = ['content']


class PostCreationForm(forms.ModelForm):
    """
    Form for creating a new blog post.
    Allows admin to enter title, slug, description, cover image, and tags.
    """
    class Meta:
        model = BlogPost
        fields = ['title_heading', 'slug', 'title_description', 'description', 'cover_image', 'tags']