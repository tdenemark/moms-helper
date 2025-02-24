from django import forms
from .models import BlogPost
from .models import Comment

print("forms loaded")
class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content':forms.Textarea(attrs = {'placeholder':'Add a comment...', 'rows':3})
        }