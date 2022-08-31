from django import forms
from .models import Post,Category


class PostForm(forms.ModelForm):
    Category = forms.CharField(max_length=100)
    class Meta:
        model = Post
        fields = [
            'author_post',
            'heading',
            'text',
        ]



