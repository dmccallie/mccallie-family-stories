from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['family_tag', 'bio', 'location', 'birth_month', 'birth_day',
                     'profile_image']
