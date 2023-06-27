from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ['content' ]
        widgets = {
            'content' : forms.Textarea(attrs={'rows': 2, 'class': 'form-control mb-2'})
        }
