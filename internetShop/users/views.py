from django.shortcuts import render, HttpResponseRedirect
from django.contrib import auth, messages
from users.models import User
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from django.urls import reverse
from products.models import Product, ProductCategory, Basket, Order
import logging

logger = logging.getLogger(__name__)

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
            logger.error(f"Ошибки при регистрации: {form.errors}")
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
            messages.success(request, "Профиль успешно обновлен!")
            return HttpResponseRedirect(reverse('users:profile'))
        else:
            logger.error(f"Ошибки в форме профиля: {form.errors}")
    else:
        form = UserProfileForm(instance=request.user)

    baskets = Basket.objects.filter(user=request.user)
    total_sum = sum(basket.sum for basket in baskets) if baskets else 0
    categories = ProductCategory.objects.all()
    # Получаем заказы, отсортированные по дате (от новых к старым)
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    # Группируем заказы по годам
    orders_by_year = {}
    for order in orders:
        year = order.order_date.year
        if year not in orders_by_year:
            orders_by_year[year] = []
        orders_by_year[year].append(order)

    context = {
        'form': form,
        'title': "Профиль",
        'baskets': baskets,
        'total_sum': total_sum,
        'categories': categories,
        'products': Product.objects.all()[:10],
        'orders_by_year': orders_by_year,
    }
    return render(request, "users/profile.html", context)

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))