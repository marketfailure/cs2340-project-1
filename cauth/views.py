from django.contrib.auth import authenticate, login, models, decorators, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIHandler
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

import cauth.forms as forms

SUCCESS_URL = '/cauth/login/'

def register(request: WSGIHandler):
    err_dict = {'action': 'register'}
    if request.method == 'POST':
        fform = forms.RegisterForm(request.POST)
        if not fform.is_valid():
            return render(request, 'error.html', err_dict | {'error': 'Form is invalid'})

        password = fform['password'].value()
        if password != fform['password_repeat'].value():
            return render(request, 'error.html', err_dict | {'error': 'Password does not match repeated password'})

        mail = fform['mail'].value()
        User = get_user_model()
        if User.objects.filter(email=mail).exists():
            return render(request, 'error.html', err_dict | {'error': 'Username exists'})

        user = User.objects.create_user(username=mail, email=mail, password=password)

        role = fform.cleaned_data["role"]
        if role == "RECRUITER":
            g, _ = Group.objects.get_or_create(name="recruiters")
            user.groups.add(g)
        else:
            g, _ = Group.objects.get_or_create(name="job_seekers")
            user.groups.add(g)
        login(request, user)

        return HttpResponseRedirect('/profiles/edit/me/')
    return render(request, 'register/index.html', {'form' : forms.RegisterForm()})

def loginpage(request: WSGIHandler):
    err_dict = {'action': 'login'}
    if request.method == 'POST':
        fform = forms.LoginForm(request.POST)
        if not fform.is_valid():
            return render(request, 'error.html', err_dict | {'error': 'Form is invalid'})

        user = authenticate(request, username=fform['mail'].value(), password=fform['password'].value())
        if user is None:
            return render(request, 'error.html', err_dict | {'error': 'User is None'})
        login(request, user)
        return HttpResponseRedirect(SUCCESS_URL)
    return render(request, 'login/index.html', {'form': forms.LoginForm()})

@decorators.login_required
def logoutpage(request: WSGIHandler):
    logout(request)
    return HttpResponseRedirect(SUCCESS_URL)
