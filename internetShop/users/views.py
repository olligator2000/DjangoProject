from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, redirect
from django.contrib import auth, messages
from django.http import JsonResponse
from users.models import User
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from django.urls import reverse
from products.models import Product, ProductCategory, Basket, Order
from users.models import Favorite


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
            messages.success(request, "Вы успешно зарегистрировались!")
            return HttpResponseRedirect(reverse('users:login'))
        else:
            logger.error(f"Ошибки при регистрации: {form.errors}")
            # Автоматически покажет ошибки из формы через form.errors
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


def add_to_favorites(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Требуется авторизация'}, status=401)

    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if created:
        return JsonResponse({'status': 'added'})
    else:
        favorite.delete()
        return JsonResponse({'status': 'removed'})


def remove_from_favorites(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Требуется авторизация'}, status=401)

    favorite = get_object_or_404(Favorite, user=request.user, product_id=product_id)
    favorite.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect(request.META.get('HTTP_REFERER', 'index'))