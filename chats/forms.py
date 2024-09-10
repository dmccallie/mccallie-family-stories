from django import forms
from chats.models import Chat, Blurb

class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['topic', 'published']
        widgets = {
            'starter': forms.HiddenInput(),  # Assuming the user link will be handled by the view,
            'topic': forms.TextInput(attrs={'placeholder': "what's this chat about?"}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ChatForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['starter'] = self.instance.starter

class BlurbForm(forms.ModelForm):
    class Meta:
        model = Blurb
        fields = ['content', 'published']
        widgets = {
            'author': forms.HiddenInput(),  # Assuming the user link will be handled by the view,
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Say something!...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(BlurbForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['author'] = self.instance.author

