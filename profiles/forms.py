from django import forms
from .models import Profile

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5}),
        }
