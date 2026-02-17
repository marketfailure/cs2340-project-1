from django import forms
from .models import Profile, Skill, Education, WorkExperience, AboutLink

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'first_name',
            'last_name',
            'headline',
            'bio',
            'avatar',
            'hide_name_from_recruiters',
            'hide_bio_from_recruiters',
            'hide_skills_from_recruiters',
            'hide_education_from_recruiters',
            'hide_work_from_recruiters',
            'hide_links_from_recruiters',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['school', 'degree', 'field_of_study', 'start_year', 'end_year']


class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ['company', 'title', 'location', 'start_date', 'end_date', 'is_current', 'description']
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}


class AboutLinkForm(forms.ModelForm):
    class Meta:
        model = AboutLink
        fields = ['label', 'url']


class RecruiterProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'headline', 'bio', 'avatar']
        widgets = {'bio': forms.Textarea(attrs={'rows': 5})}
