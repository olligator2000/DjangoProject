from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from products.models import Product, ProductCategory, Basket, Order, OrderItem
from products.forms import OrderForm
from django.views.generic import ListView
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

class IndexView(ListView):
    template_name = 'products/index.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.order_by('?')[:4]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.all()
        context['baskets'] = Basket.objects.filter(user=self.request.user) if self.request.user.is_authenticated else []
        context['total_sum'] = sum(basket.sum for basket in context['baskets']) if context['baskets'] else 0
        return context

def get_random_products(request):
    products = Product.objects.order_by('?')[:4]  # Теперь точно 4 товара
    html = render_to_string('products/partial_carousel.html', {'products': products})
    return JsonResponse({'carousel_html': html})

def index(request):
    categories = ProductCategory.objects.prefetch_related('products').all()
    first_category = categories.first()

    baskets = Basket.objects.filter(user=request.user) if request.user.is_authenticated else []
    total_sum = sum(basket.sum for basket in baskets) if baskets else 0

    context = {
        "title": "store",
        "categories": categories,
        "products": first_category.products.all() if first_category else [],
        "show_products": False,
        'baskets': baskets,
        'total_sum': total_sum,
    }
    return render(request, "products/index.html", context)

def products(request):
    categories = ProductCategory.objects.prefetch_related('products').all()  # Добавляем категории
    first_category = categories.first()
    baskets = Basket.objects.filter(user=request.user) if request.user.is_authenticated else []
    total_sum = sum(basket.sum for basket in baskets) if baskets else 0

    context = {
        "title": "store - products",
        'baskets': baskets,
        'total_sum': total_sum,
        "categories": categories,
        "products": first_category.products.all() if first_category else [],
    }
    return render(request, "products/products.html", context)


def category_products(request, category_id):
    category = get_object_or_404(ProductCategory, id=category_id)
    products = Product.objects.filter(category=category)
    brands = products.values_list('brand', flat=True).distinct()
    manufacturers = products.values_list('manufacturer', flat=True).distinct()
    categories = ProductCategory.objects.prefetch_related('products').all()

    baskets = Basket.objects.filter(user=request.user) if request.user.is_authenticated else []
    total_sum = sum(basket.sum for basket in baskets) if baskets else 0

    context = {
        "title": f"Товары категории {category.name}",
        "category": category,
        "products": products,
        "brands": brands,
        "manufacturers": manufacturers,
        'baskets': baskets,
        'total_sum': total_sum,
        "categories": categories,
    }
    return render(request, "products/products.html", context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    category = product.category
    categories = ProductCategory.objects.prefetch_related('products').all()
    first_category = categories.first()
    baskets = Basket.objects.filter(user=request.user) if request.user.is_authenticated else []
    total_sum = sum(basket.sum for basket in baskets) if baskets else 0

    context = {
        "title": product.name,
        "product": product,
        "category": category,
        "categories": categories,
        "products": first_category.products.all() if first_category else [],
        'baskets': baskets,
        'total_sum': total_sum,
    }
    return render(request, "products/products_list.html", context)

def products_list(request):
    categories = ProductCategory.objects.prefetch_related('products').all()
    first_category = categories.first()
    baskets = Basket.objects.filter(user=request.user) if request.user.is_authenticated else []
    total_sum = sum(basket.sum for basket in baskets) if baskets else 0

    context = {
        "title": "Описание продукта",
        "categories": categories,
        "products": first_category.products.all() if first_category else [],
        "show_products": False,
        'baskets': baskets,
        'total_sum': total_sum,
    }

    return render(request, "products/products_list.html", context)


def get_products_by_category(request):
    category_id = request.GET.get('category_id')
    products = Product.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(products), safe=False)


def search_products(request):
    try:
        query = request.GET.get('q', '').strip()
        if not query or len(query) < 2:
            return JsonResponse({'categories': [], 'products': []})

        # Поиск категорий
        categories = ProductCategory.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).values('id', 'name')[:1]

        # Поиск товаров
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query) |
            Q(manufacturer__icontains=query)
        ).values('id', 'name', 'image', 'price')[:10]

        # Формирование списка категорий
        categories_list = list(categories)
        for category in categories_list:
            category['type'] = 'category'

        # Формирование списка товаров
        products_list = list(products)
        for product in products_list:
            product['type'] = 'product'
            # Проверяем, есть ли изображение
            if product['image']:  # Проверяем, не пустое ли поле image
                try:
                    # Предполагаем, что image уже строка (путь к файлу), так как используется .values()
                    product['image'] = request.build_absolute_uri('/media/' + product['image'])
                    logger.debug(f"Изображение для продукта {product['id']}: {product['image']}")
                except Exception as e:
                    logger.warning(f"Ошибка при обработке изображения для продукта {product['id']}: {str(e)}")
                    product['image'] = request.build_absolute_uri('/static/images/placeholder.png')
            else:
                logger.debug(f"Изображение отсутствует для продукта {product['id']}")
                product['image'] = request.build_absolute_uri('/static/images/placeholder.png')

        # Объединяем категории и товары
        results = categories_list + products_list

        logger.info(f"Поисковый запрос: '{query}', найдено категорий: {len(categories_list)}, товаров: {len(products_list)}")
        return JsonResponse({'results': results})

    except Exception as e:
        logger.error(f"Ошибка при поиске товаров: {str(e)}", exc_info=True)
        return JsonResponse({'results': []}, status=500)


@login_required
def add_to_cart_ajax(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)

        # Проверка: товар отсутствует на складе
        if product.quantity <= 0:
            logger.warning(f"Попытка добавить отсутствующий товар: {product_id}")
            return JsonResponse({
                'status': 'error',
                'message': 'Товар отсутствует на складе'
            }, status=400)

        basket, created = Basket.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 1}
        )

        if not created:
            # Проверка: достаточно ли товара на складе
            if product.quantity <= basket.quantity:
                logger.warning(f"Недостаточно товара: {product_id} (доступно: {product.quantity}, в корзине: {basket.quantity})")
                return JsonResponse({
                    'status': 'error',
                    'message': f'Недостаточно товара на складе. Доступно: {product.quantity}'
                }, status=400)
            basket.quantity += 1
            basket.save()

        baskets = Basket.objects.filter(user=request.user)
        total_sum = sum(basket.sum for basket in baskets) if baskets else 0

        return JsonResponse({
            'status': 'success',
            'cart_html': render_to_string('products/basket.html', {
                'baskets': baskets,
                'total_sum': total_sum
            }),
            'total_items': baskets.count(),
            'total_sum': float(total_sum)
        })

    except Exception as e:
        logger.error(f"Ошибка при добавлении товара в корзину: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': 'Внутренняя ошибка сервера'
        }, status=500)

@login_required
def update_basket_ajax(request, basket_id, action):
    try:
        # Получаем объект корзины
        basket = get_object_or_404(Basket, id=basket_id, user=request.user)
        if not basket.product:
            logger.error(f"Продукт для корзины {basket_id} не найден")
            return JsonResponse({
                'status': 'error',
                'message': 'Продукт не найден'
            }, status=400)

        product = get_object_or_404(Product, id=basket.product.id)

        if action == 'increase':
            if product.quantity <= basket.quantity:
                logger.warning(f"Недостаточно товара: {product.id} (доступно: {product.quantity}, в корзине: {basket.quantity})")
                return JsonResponse({
                    'status': 'error',
                    'message': f'Недостаточно товара на складе. Доступно: {product.quantity}'
                }, status=400)
            basket.quantity += 1
        elif action == 'decrease':
            if basket.quantity <= 1:
                basket.delete()
                baskets = Basket.objects.filter(user=request.user)
                return JsonResponse({
                    'status': 'removed',
                    'basket_id': basket_id,
                    'total_sum': float(sum(b.sum for b in baskets) or 0)
                })
            basket.quantity -= 1
        else:
            logger.error(f"Недопустимое действие: {action} для корзины {basket_id}")
            return JsonResponse({
                'status': 'error',
                'message': 'Недопустимое действие'
            }, status=400)

        basket.save()

        baskets = Basket.objects.filter(user=request.user)
        total_sum = sum(b.sum for b in baskets) or 0

        return JsonResponse({
            'status': 'success',
            'basket_id': basket.id,
            'quantity': basket.quantity,
            'sum': float(basket.sum),
            'total_sum': float(total_sum)
        })

    except Product.DoesNotExist:
        logger.error(f"Продукт с ID {basket.product.id if basket else 'unknown'} не найден для корзины {basket_id}")
        return JsonResponse({
            'status': 'error',
            'message': 'Продукт не найден'
        }, status=400)
    except Exception as e:
        logger.error(f"Ошибка при обновлении корзины {basket_id}: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': f'Внутренняя ошибка сервера: {str(e)}'
        }, status=500)

@login_required
def clear_basket_ajax(request):
    try:
        deleted_count, _ = Basket.objects.filter(user=request.user).delete()

        if deleted_count == 0:
            return JsonResponse({
                'status': 'empty',
                'message': 'Корзина уже была пуста'
            })

        return JsonResponse({
            'status': 'success',
            'cart_html': render_to_string('products/basket.html', {
                'baskets': [],
                'total_sum': 0
            }),
            'total_sum': 0
        })

    except Exception as e:
        logger.error(f"Ошибка при очистке корзины: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': 'Не удалось очистить корзину'
        }, status=500)


@login_required
def zakaz_end(request):
    baskets = Basket.objects.filter(user=request.user) if request.user.is_authenticated else []
    total_sum = sum(basket.sum for basket in baskets) if baskets else 0
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            if not baskets.exists():
                messages.error(request, 'Корзина пуста!')
                return redirect('products:index')
            order.total_price = total_sum
            order.save()
            for basket in baskets:
                OrderItem.objects.create(
                    order=order,
                    product=basket.product,
                    quantity=basket.quantity,
                    price=basket.product.price
                )
            baskets.delete()
            messages.success(request, 'Заказ успешно создан!')
            return redirect('products:order_confirmation')
    else:
        form = OrderForm(initial={'total_price': total_sum, 'delivery_cost': 0, 'service_fee': 39})
    context = {
        'form': form,
        'basket_items': baskets,
        'total_sum': total_sum,
        'categories': ProductCategory.objects.all(),
    }
    return render(request, 'products/zakaz_end.html', context)


@login_required
def get_cart_state(request):
    try:
        baskets = Basket.objects.filter(user=request.user)
        total_sum = sum(basket.sum for basket in baskets) if baskets else 0
        cart_html = render_to_string('products/basket.html', {'baskets': baskets, 'total_sum': total_sum})
        return JsonResponse({
            'total_items': baskets.count(),
            'total_sum': float(total_sum),
            'cart_html': cart_html
        })
    except Exception as e:
        logger.error(f"Ошибка при синхронизации корзины: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Ошибка синхронизации корзины'}, status=500)