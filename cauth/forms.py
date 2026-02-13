from django import forms

class RegisterForm(forms.Form):
    mail = forms.CharField(label="Mail", max_length=255)
    password = forms.CharField(label="Password", widget=forms.PasswordInput(), max_length=63)
    password_repeat = forms.CharField(label="Password Repeat", widget=forms.PasswordInput(), max_length=63)

class LoginForm(forms.Form):
    mail = forms.CharField(label="Mail", max_length=63)
    password = forms.CharField(label="Password", widget=forms.PasswordInput(), max_length=63)
