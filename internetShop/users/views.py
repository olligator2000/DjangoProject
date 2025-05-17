from django.shortcuts import render, HttpResponseRedirect
from django.contrib import auth
from users.models import User
from users.forms import UserLoginForm
from django.urls import reverse


def login(request):

    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
    else:
        form = UserLoginForm()

    context = {
        "title": "store - login",
        "form": form,
    }
    return render(request, "users/login.html", context)


def register(request):
    context = {
        "title": "store - register",
    }
    return render(request, "users/register.html", context)
