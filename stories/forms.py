from django import forms
from .models import Story, Comment
from .markdownit import md  # Import the configured MarkdownIt instance
from django.conf import settings

class StoryForm(forms.ModelForm):
    tags = forms.MultipleChoiceField(
        choices=[(tag, tag) for tag in settings.STANDARD_TAGS],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = Story
        # todo rename user to author
        fields = ['title', 'content', 'summary', 'image', 'user', 'tags']
        widgets = {
            'published_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'user': forms.HiddenInput(),  # Assuming the user link will be handled by the view,
            'title': forms.TextInput(attrs={'placeholder': 'enter title here'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(StoryForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['tags'] = [tag.name for tag in self.instance.tags.all()]

    
    # def save(self, commit=True):
    #     instance = super(StoryForm, self).save(commit=False)
    #     if commit:
    #         instance.save()
    #         instance.tags.set(*self.cleaned_data['tags'])
    #     return instance

    # def save_m2m(self):
    #     """
    #     Save many-to-many relationships for the instance. 
    #     This method is called when commit=False in the save method.
    #     """
    #     super(StoryForm, self).save_m2m()
    #     self.instance.tags.set(*self.cleaned_data['tags'])


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 1, 'placeholder': 'Add a comment...'}),
        }