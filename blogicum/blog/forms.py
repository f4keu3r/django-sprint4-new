from django import forms
from django.core.exceptions import ValidationError

from .models import Post, Comment
from core.constants import MODERATION_ERROR
from .moderation import is_toxic


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'pub_date',
            'category',
            'location',
            'image',
        )
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pub_date'].input_formats = ('%Y-%m-%dT%H:%M',)


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if is_toxic(text):
            raise ValidationError(MODERATION_ERROR)
        return text
