import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from products.models import Product, ProductCategory, Basket

# Настройка логирования
logger = logging.getLogger(__name__)

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
        basket = get_object_or_404(Basket, id=basket_id, user=request.user)
        product = get_object_or_404(Product, id=basket.product.id)

        if action == 'increase':
            # Проверка: достаточно ли товара на складе
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
                return JsonResponse({
                    'status': 'removed',
                    'basket_id': basket_id,
                    'total_sum': float(sum(b.sum for b in Basket.objects.filter(user=request.user)) or 0)
                })
            basket.quantity -= 1

        basket.save()

        return JsonResponse({
            'status': 'success',
            'basket_id': basket.id,
            'quantity': basket.quantity,
            'sum': float(basket.sum),
            'total_sum': float(sum(b.sum for b in Basket.objects.filter(user=request.user)) or 0)
        })

    except Exception as e:
        logger.error(f"Ошибка при обновлении корзины: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': 'Внутренняя ошибка сервера'
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