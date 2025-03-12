from django import forms
from .models import Comment, BlogPost


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4,}),
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class PostCreationForm(forms.ModelForm):

    class Meta:
        model = BlogPost
        fields = ['title_heading', 'slug', 'title_description', 'description', 'cover_image', 'tags']