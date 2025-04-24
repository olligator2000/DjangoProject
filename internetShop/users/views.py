from django.shortcuts import render
from users.models import User


def login(request):
    context = {
        "title": "store - login",
    }
    return render(request, "users/login.html", context)


def register(request):
    context = {
        "title": "store - register",
    }
    return render(request, "users/register.html", context)
