from django.contrib.auth import authenticate, login, models, decorators, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIHandler
from django.contrib.auth import get_user_model

import cauth.forms as forms

SUCCESS_URL = '/feed/'

def register(request: WSGIHandler):
    err_dict = {'action': 'register'}
    if request.method == 'POST':
        fform = forms.RegisterForm(request.POST)
        if not fform.is_valid():
            return render(request, 'error.html', err_dict | {'type': 'Form is invalid'})

        password = fform['password'].value()
        if password != fform['password_repeat'].value():
            return render(request, 'error.html', err_dict | {'error': 'Password does not match repeated password'})

        username = fform['username'].value()
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return render(request, 'error.html', err_dict | {'error': 'Username exists'})

        user = User.objects.create_user(username=username, email=fform['mail'].value(), password=password)
        login(request, user)
        return HttpResponseRedirect(SUCCESS_URL)
    return render(request, 'register/index.html', {'form' : forms.RegisterForm})

def loginpage(request: WSGIHandler):
    err_dict = {'action': 'login'}
    if request.method == 'POST':
        fform = forms.LoginForm(request.POST)
        if not fform.is_valid():
            return render(request, 'error.html', err_dict | {'error': 'Form is invalid'})

        user = authenticate(request, username=fform['username'].value(), password=fform['password'].value())
        if user is None:
            return render(request, 'error.html', err_dict | {'error': 'Form is invalid'})
        login(request, user)
        return HttpResponseRedirect(SUCCESS_URL)
    return render(request, 'login/index.html', {'form': forms.LoginForm})

@decorators.login_required
def logoutpage(request: WSGIHandler):
    logout(request)
    return HttpResponseRedirect(SUCCESS_URL)
