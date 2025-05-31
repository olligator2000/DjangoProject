from django.shortcuts import render, HttpResponseRedirect
from django.contrib import auth, messages
from users.models import User
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from django.urls import reverse
from products.models import Product, ProductCategory, Basket


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
        "title": "Авторизация",
        "form": form,
    }
    return render(request, "users/login.html", context)


def register(request):

    if request.method == "POST":
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, message="Вы успешно зарегистрировались!")
            return HttpResponseRedirect(reverse('users:login'))
        else:
            print(form.errors)
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
        "title": "Регистрация",
    }
    return render(request, "users/register.html", context)


def profile(request):
    if request.method == "POST":
        form = UserProfileForm(data=request.POST, instance=request.user, files=request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('users:profile'))
        else:
            print(form.errors)
    else:
        form = UserProfileForm(instance=request.user)

    baskets = Basket.objects.filter(user=request.user)
    total_sum = sum(basket.sum for basket in baskets) if baskets else 0
    categories = ProductCategory.objects.all()  # Добавляем категории

    context = {
        'form': form,
        'title': "Профиль",
        'baskets': baskets,
        'total_sum': total_sum,
        'categories': categories,  # Добавляем в контекст
        'products': Product.objects.all()[:10],  # Добавляем продукты (можно ограничить)
    }
    return render(request, "users/profile.html", context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))
