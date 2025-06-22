from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from products.models import Product, ProductCategory, Basket, Order, OrderItem, ProductRating, ProductReview
from products.forms import OrderForm, ReviewForm
from django.views.generic import ListView
from django.db.models import Q
from django.db import transaction
from users.models import Favorite
from django.db.models.functions import Collate
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
    if request.method == 'POST':
        try:
            # Получаем 4 случайных продукта, у которых есть количество на складе
            products = Product.objects.filter(quantity__gt=0).order_by('?')[:4]

            # Получаем favorite_ids для авторизованного пользователя
            favorite_ids = []
            if request.user.is_authenticated:
                favorite_ids = request.user.favorites.values_list('product_id', flat=True)

            html = render_to_string('products/partial_carousel.html', {
                'products': products,
                'favorite_ids': favorite_ids,
                'request': request  # Передаем request в контекст
            })
            return JsonResponse({'carousel_html': html})
        except Exception as e:
            logger.error(f"Ошибка при получении случайных товаров: {str(e)}", exc_info=True)
            return JsonResponse({'error': 'Ошибка сервера'}, status=500)
    return JsonResponse({'error': 'Недопустимый метод'}, status=400)

def index(request):
    categories = ProductCategory.objects.prefetch_related('products').all()
    first_category = categories.first()

    baskets = Basket.objects.filter(user=request.user) if request.user.is_authenticated else []
    total_sum = sum(basket.sum for basket in baskets) if baskets else 0


    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = request.user.favorites.values_list('product_id', flat=True)

    context = {
        "title": "store",
        "categories": categories,
        "products": first_category.products.all() if first_category else [],
        "show_products": False,
        'baskets': baskets,
        'total_sum': total_sum,
        'favorite_ids': favorite_ids,

    }
    return render(request, "products/index.html", context)

def products(request):
    categories = ProductCategory.objects.prefetch_related('products').all()
    first_category = categories.first() if categories.exists() else None
    baskets = Basket.objects.filter(user=request.user) if request.user.is_authenticated else []
    total_sum = sum(basket.sum for basket in baskets) if baskets else 0

    # Получаем все бренды и производители из всех продуктов
    brands = Product.objects.values_list('brand', flat=True).distinct()
    manufacturers = Product.objects.values_list('manufacturer', flat=True).distinct()

    # Получаем favorite_ids для авторизованного пользователя
    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = request.user.favorites.values_list('product_id', flat=True)

    context = {
        "title": "store - products",
        'baskets': baskets,
        'total_sum': total_sum,
        "categories": categories,
        "products": first_category.products.all() if first_category else [],
        "category": first_category,
        "brands": brands,
        "manufacturers": manufacturers,
        'favorite_ids': favorite_ids,  # Добавляем favorite_ids в контекст
    }
    return render(request, "products/products.html", context)

def category_products(request, category_id):
    category = get_object_or_404(ProductCategory, id=category_id)
    products = Product.objects.filter(category=category)

    # Обработка фильтров
    brands = request.GET.getlist('brand')
    manufacturers = request.GET.getlist('manufacturer')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if brands:
        products = products.filter(brand__in=brands)
    if manufacturers:
        products = products.filter(manufacturer__in=manufacturers)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Обработка сортировки
    sort = request.GET.get('sort', 'price_asc')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'brand_asc':
        products = products.order_by('brand')
    elif sort == 'brand_desc':
        products = products.order_by('-brand')
    elif sort == 'manufacturer_asc':
        products = products.order_by('manufacturer')
    elif sort == 'manufacturer_desc':
        products = products.order_by('-manufacturer')
    elif sort == 'rating':
        products = products.order_by('-average_rating')
    elif sort == 'popularity':
        products = products.order_by('-quantity')
    else:
        products = products.order_by('price')

    brands = Product.objects.filter(category=category).values_list('brand', flat=True).distinct()
    manufacturers = Product.objects.filter(category=category).values_list('manufacturer', flat=True).distinct()
    categories = ProductCategory.objects.prefetch_related('products').all()

    baskets = Basket.objects.filter(user=request.user) if request.user.is_authenticated else []
    total_sum = sum(basket.sum for basket in baskets) if baskets else 0

    # Получаем favorite_ids для авторизованного пользователя
    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = request.user.favorites.values_list('product_id', flat=True)

    context = {
        "title": f"Товары категории {category.name}",
        "category": category,
        "products": products,
        "brands": brands,
        "manufacturers": manufacturers,
        "sort": sort,
        'baskets': baskets,
        'total_sum': total_sum,
        "categories": categories,
        'favorite_ids': favorite_ids,  # Добавляем favorite_ids в контекст
    }
    return render(request, "products/products.html", context)

def filter_products(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            category_id = data.get('category_id')
            brands = data.get('brand', [])
            manufacturers = data.get('manufacturer', [])
            min_price = data.get('min_price')
            max_price = data.get('max_price')
            sort = data.get('sort', 'price_asc')

            # Получаем favorite_ids для авторизованного пользователя
            favorite_ids = []
            if request.user.is_authenticated:
                favorite_ids = request.user.favorites.values_list('product_id', flat=True)

            # Если category_id не указан, берем все продукты
            if category_id:
                category = get_object_or_404(ProductCategory, id=category_id)
                products = Product.objects.filter(category=category)
            else:
                products = Product.objects.all()

            # Остальной код обработки фильтров и сортировки остается без изменений
            if brands:
                products = products.filter(brand__in=brands)
            if manufacturers:
                products = products.filter(manufacturer__in=manufacturers)
            if min_price:
                products = products.filter(price__gte=float(min_price))
            if max_price:
                products = products.filter(price__lte=float(max_price))

            # Обработка сортировки
            if sort == 'price_asc':
                products = products.order_by('price')
            elif sort == 'price_desc':
                products = products.order_by('-price')
            elif sort == 'brand_asc':
                products = products.order_by('brand')
            elif sort == 'brand_desc':
                products = products.order_by('-brand')
            elif sort == 'manufacturer_asc':
                products = products.order_by('manufacturer')
            elif sort == 'manufacturer_desc':
                products = products.order_by('-manufacturer')
            elif sort == 'rating':
                products = products.order_by('-average_rating')
            elif sort == 'popularity':
                products = products.order_by('-quantity')
            else:
                products = products.order_by('price')

            products_html = render_to_string('products/products_grid_partial.html', {
                'products': products,
                'favorite_ids': favorite_ids,
                'request': request
            })

            return JsonResponse({
                'status': 'success',
                'products_html': products_html
            })
        except Exception as e:
            logger.error(f"Ошибка при фильтрации товаров: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': 'Ошибка фильтрации'
            }, status=500)
    return JsonResponse({
        'status': 'error',
        'message': 'Недопустимый метод'
    }, status=400)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    category = product.category
    categories = ProductCategory.objects.prefetch_related('products').all()
    first_category = categories.first()
    baskets = Basket.objects.filter(user=request.user) if request.user.is_authenticated else []
    total_sum = sum(basket.sum for basket in baskets) if baskets else 0
    reviews = product.reviews.all().order_by('-created_at').select_related('user')

    # Проверяем, может ли пользователь оценивать товар
    user_can_rate = False
    user_rating = 0
    if request.user.is_authenticated:
        # Проверяем, есть ли товар в заказах пользователя
        has_ordered = OrderItem.objects.filter(
            order__user=request.user,
            product=product
        ).exists()

        if has_ordered:
            user_can_rate = True
            # Получаем текущую оценку пользователя, если есть
            try:
                rating = ProductRating.objects.get(user=request.user, product=product)
                user_rating = rating.rating
            except ProductRating.DoesNotExist:
                pass

        # Получаем список ID избранных товаров пользователя
        favorite_ids = request.user.favorites.values_list('product_id', flat=True)
    else:
        favorite_ids = []

    # Проверка возможности оставить отзыв
    can_review = False
    if request.user.is_authenticated:
        can_review = OrderItem.objects.filter(
            order__user=request.user,
            product=product
        ).exists()

    # Обработка отправки отзыва
    review_form = None
    if request.method == 'POST' and 'review_text' in request.POST:
        if can_review:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.user = request.user
                review.product = product
                review.save()
                messages.success(request, 'Ваш отзыв успешно добавлен!')
                return redirect('products:product_detail', product_id=product.id)
        else:
            messages.error(request, 'Вы не можете оставить отзыв, так как не покупали этот товар')
    else:
        review_form = ReviewForm()

    context = {
        "title": product.name,
        "product": product,
        "category": category,
        "categories": categories,
        "products": first_category.products.all() if first_category else [],
        'baskets': baskets,
        'total_sum': total_sum,
        'user_can_rate': user_can_rate,
        'user_rating': user_rating,
        'can_review': can_review,
        'review_form': review_form,
        'reviews': reviews,
        'favorite_ids': list(favorite_ids),  # Добавляем список ID избранных товаров
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'products/right_column_partial.html', context)
    return render(request, 'products/products_list.html', context)

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

        categories = ProductCategory.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).values('id', 'name')[:1]

        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query) |
            Q(manufacturer__icontains=query)
        ).values('id', 'name', 'image', 'price')[:10]

        categories_list = list(categories)
        for category in categories_list:
            category['type'] = 'category'

        products_list = list(products)
        for product in products_list:
            product['type'] = 'product'
            if product['image']:
                try:
                    product['image'] = request.build_absolute_uri('/media/' + product['image'])
                    logger.debug(f"Изображение для продукта {product['id']}: {product['image']}")
                except Exception as e:
                    logger.warning(f"Ошибка при обработке изображения для продукта {product['id']}: {str(e)}")
                    product['image'] = request.build_absolute_uri('/static/images/placeholder.png')
            else:
                logger.debug(f"Изображение отсутствует для продукта {product['id']}")
                product['image'] = request.build_absolute_uri('/static/images/placeholder.png')

        results = categories_list + products_list

        logger.info(f"Поисковый запрос: '{query}', найдено категорий: {len(categories_list)}, товаров: {len(products_list)}")
        return JsonResponse({'results': results})

    except Exception as e:
        logger.error(f"Ошибка при поиске товаров: {str(e)}", exc_info=True)
        return JsonResponse({'results': []}, status=500)

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


@login_required
def add_to_cart_ajax(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)

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
            if product.quantity <= basket.quantity:
                logger.warning(
                    f"Недостаточно товара: {product_id} (доступно: {product.quantity}, в корзине: {basket.quantity})")
                return JsonResponse({
                    'status': 'error',
                    'message': f'Недостаточно товара на складе. Доступно: {product.quantity}'
                }, status=400)
            basket.quantity += 1
            basket.save()

        baskets = Basket.objects.filter(user=request.user)
        total_sum = sum(basket.sum for basket in baskets) if baskets else 0
        delivery_cost = 0 if total_sum < 1000 else int(total_sum * 0.10)

        return JsonResponse({
            'status': 'success',
            'cart_html': render_to_string('products/basket.html', {
                'baskets': baskets,
                'total_sum': total_sum,
                'delivery_cost': delivery_cost
            }),
            'total_items': baskets.count(),
            'total_sum': float(total_sum),
            'delivery_cost': float(delivery_cost)
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

def process_payment(payment_method, card_details, total_amount):
    logger.info(f"Обработка платежа через {payment_method} на сумму {total_amount}")
    try:
        if payment_method == 'card':
            card_number = card_details.get('card_number', '')
            cardholder_name = card_details.get('cardholder_name', '')
            cvv = card_details.get('cvv', '')
            card_number = card_number.replace(' ', '').replace('-', '')
            if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
                raise ValueError('Неверный номер карты')
            if not cardholder_name or not all(part[0].isupper() for part in cardholder_name.split() if part):
                raise ValueError('Неверное имя держателя карты')
            if not cvv.isdigit() or len(cvv) not in (3, 4):
                raise ValueError('Неверный CVV')
            return {'status': 'success', 'transaction_id': f'TXN-{int(total_amount * 100)}-{card_number[-4:]}'}
        elif payment_method == 'sbp':
            return {'status': 'success', 'transaction_id': f'SBP-TXN-{int(total_amount * 100)}'}
        else:
            raise ValueError('Недопустимый способ оплаты')
    except ValueError as e:
        logger.error(f"Ошибка валидации платежа: {str(e)}")
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        logger.error(f"Ошибка обработки платежа: {str(e)}")
        return {'status': 'error', 'message': 'Ошибка обработки платежа'}

@login_required
def zakaz_end(request):
    baskets = Basket.objects.filter(user=request.user) if request.user.is_authenticated else []
    total_sum = sum(basket.sum for basket in baskets) if baskets else 0

    if total_sum < 1000:
        delivery_cost = 0
    else:
        delivery_cost = int(total_sum * 0.10)
    service_fee = 39
    total_with_delivery = total_sum + delivery_cost + service_fee

    if request.method == 'POST':
        logger.info(f"POST запрос на zakaz_end, данные: {request.POST}")
        payment_method = request.POST.get('payment_method', '')
        logger.info(f"Выбранный способ оплаты: {payment_method}")

        if not payment_method:
            logger.warning("Способ оплаты не выбран")
            messages.error(request, 'Выберите способ оплаты')
            return redirect('products:zakaz_end')

        form = OrderForm(request.POST)
        if form.is_valid():
            logger.info("Форма валидна")
            try:
                with transaction.atomic():
                    if payment_method == 'card':
                        card_details = {
                            'card_number': form.cleaned_data.get('card_number', ''),
                            'cardholder_name': form.cleaned_data.get('cardholder_name', ''),
                            'cvv': form.cleaned_data.get('cvv', '')
                        }
                        logger.info(f"Данные карты: {card_details}")
                        payment_result = process_payment(payment_method, card_details, total_with_delivery)
                    else:
                        payment_result = process_payment(payment_method, {}, total_with_delivery)

                    if payment_result['status'] == 'error':
                        logger.error(f"Ошибка платежа: {payment_result['message']}")
                        messages.error(request, payment_result['message'])
                        return redirect('products:zakaz_end')

                    order = form.save(commit=False)
                    order.user = request.user
                    if not baskets.exists():
                        logger.warning("Корзина пуста")
                        messages.error(request, 'Корзина пуста!')
                        return redirect('products:zakaz_end')

                    order.total_price = total_sum
                    order.delivery_cost = delivery_cost
                    order.service_fee = service_fee
                    order.payment_method = payment_method
                    order.transaction_id = payment_result['transaction_id']
                    order.save()

                    for basket in baskets:
                        OrderItem.objects.create(
                            order=order,
                            product=basket.product,
                            quantity=basket.quantity,
                            price=basket.product.price
                        )

                    logger.info(f"Заказ #{order.id} успешно создан, очищаем корзину")
                    baskets.delete()
                    messages.success(request, f'Заказ успешно создан! ID транзакции: {payment_result["transaction_id"]}')
                    return redirect('products:order_confirmation')
            except Exception as e:
                logger.error(f"Ошибка при создании заказа: {str(e)}", exc_info=True)
                messages.error(request, 'Произошла ошибка при оформлении заказа. Пожалуйста, попробуйте еще раз.')
                return redirect('products:zakaz_end')
        else:
            logger.error(f"Форма невалидна: {form.errors.as_json()}")
            messages.error(request, f'Ошибки в форме: {form.errors.as_text()}')
            return render(request, 'products/zakaz_end.html', {
                'form': form,
                'basket_items': baskets,
                'total_sum': total_sum,
                'delivery_cost': delivery_cost,
                'service_fee': service_fee,
                'total_with_delivery': total_with_delivery,
                'categories': ProductCategory.objects.all(),
            })
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'full_name': f"{request.user.first_name} {request.user.last_name}",
                'phone': request.user.phone if hasattr(request.user, 'phone') else '+7',
                'address': request.user.address if hasattr(request.user, 'address') else '',
                'payment_method': ''
            }
        form = OrderForm(initial=initial_data)

    context = {
        'form': form,
        'basket_items': baskets,
        'total_sum': total_sum,
        'delivery_cost': delivery_cost,
        'service_fee': service_fee,
        'total_with_delivery': total_with_delivery,
        'categories': ProductCategory.objects.all(),
    }
    logger.info("Отображение страницы zakaz_end для GET запроса")
    return render(request, 'products/zakaz_end.html', context)

@login_required
def order_confirmation(request):
    last_order = Order.objects.filter(user=request.user).order_by('-order_date').first()

    if not last_order:
        messages.warning(request, 'У вас нет активных заказов.')
        return redirect('products:index')

    context = {
        'order': last_order,
        'categories': ProductCategory.objects.all(),
    }
    return render(request, 'products/order_confirmation.html', context)

@login_required
def get_cart_state(request):
    try:
        baskets = Basket.objects.filter(user=request.user)
        total_sum = sum(basket.sum for basket in baskets) if baskets else 0
        delivery_cost = 0 if total_sum < 1000 else int(total_sum * 0.10)
        cart_html = render_to_string('products/basket.html', {
            'baskets': baskets,
            'total_sum': total_sum,
            'delivery_cost': delivery_cost
        })
        return JsonResponse({
            'total_items': baskets.count(),
            'total_sum': float(total_sum),
            'delivery_cost': float(delivery_cost),
            'cart_html': cart_html
        })
    except Exception as e:
        logger.error(f"Ошибка при синхронизации корзины: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Ошибка синхронизации корзины'}, status=500)


@login_required
def rate_product(request, product_id=None):
    if request.method == 'POST':
        try:
            # Для совместимости с обоими URL
            product_id = product_id or request.POST.get('product_id')
            rating = int(request.POST.get('rating'))

            if not (1 <= rating <= 5):
                return JsonResponse({'status': 'error', 'message': 'Недопустимая оценка'}, status=400)

            product = get_object_or_404(Product, id=product_id)

            # Проверяем, покупал ли пользователь товар
            has_ordered = OrderItem.objects.filter(
                order__user=request.user,
                product=product
            ).exists()

            if not has_ordered:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Вы не можете оценить товар, так как не покупали его'
                }, status=403)

            ProductRating.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={'rating': rating}
            )
            product.update_average_rating()

            return JsonResponse({
                'status': 'success',
                'average_rating': float(product.average_rating),
                'message': 'Оценка сохранена'
            })
        except Exception as e:
            logger.error(f"Ошибка при сохранении рейтинга: {str(e)}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Ошибка сервера'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Недопустимый метод'}, status=400)

@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Проверяем, покупал ли пользователь товар
    has_ordered = OrderItem.objects.filter(
        order__user=request.user,
        product=product
    ).exists()

    if not has_ordered:
        return JsonResponse({
            'status': 'error',
            'message': 'Вы не можете оставить отзыв, так как не покупали этот товар'
        }, status=403)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()

            # Обновляем рейтинг, если он был указан
            rating = form.cleaned_data.get('rating')
            if rating:
                ProductRating.objects.update_or_create(
                    user=request.user,
                    product=product,
                    defaults={'rating': rating}
                )
                product.update_average_rating()

            return JsonResponse({
                'status': 'success',
                'message': 'Отзыв успешно добавлен'
            })
        else:
            # Добавляем более детальную информацию об ошибках
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
            return JsonResponse({
                'status': 'error',
                'message': 'Ошибка в форме',
                'errors': errors
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Недопустимый метод'
    }, status=405)