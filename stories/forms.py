from django import forms
from .models import Story, Comment
from .markdownit import md  # Import the configured MarkdownIt instance

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        # todo rename user to author
        fields = ['title', 'content', 'summary', 'image', 'user']
        widgets = {
            'published_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'user': forms.HiddenInput(),  # Assuming the user link will be handled by the view,
            'title': forms.TextInput(attrs={'placeholder': 'enter title here'}),
        }

# class StoryForm(forms.ModelForm):
#     content_html = forms.CharField(widget=forms.Textarea, required=False)  # Transient field fpr converting markdown to html

#     class Meta:
#         model = Story
#         # todo rename user to author
#         fields = ['id', 'title', 'content', 'summary', 'image', 'user']
#         widgets = {
#             'published_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#             'user': forms.HiddenInput(),  # Assuming the user link will be handled by the view,
#             'title': forms.TextInput(attrs={'placeholder': 'enter title here'}),
#         }

#     # on fetch of form, convert markdown content to html
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if 'instance' in kwargs and kwargs['instance']:
#             instance = kwargs['instance']
#             if instance.content:
#                 self.fields['content_html'].initial = md.render(instance.content)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 1, 'placeholder': 'Add a comment...'}),
        }