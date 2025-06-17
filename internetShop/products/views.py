from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from products.models import Product, ProductCategory, Basket, Order, OrderItem
from products.forms import OrderForm
from django.views.generic import ListView
from django.db.models import Q
from django.db import transaction
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


def process_payment(payment_method, card_details, total_amount):
    """Фиктивная функция обработки платежа."""
    logger.info(f"Обработка платежа через {payment_method} на сумму {total_amount}")
    try:
        if payment_method == 'card':
            card_number = card_details.get('card_number', '')
            cardholder_name = card_details.get('cardholder_name', '')
            cvv = card_details.get('cvv', '')
            # Проверка валидности номера карты
            card_number = card_number.replace(' ', '').replace('-', '')
            if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
                raise ValueError('Неверный номер карты')
            # Проверка имени держателя карты
            if not cardholder_name or not all(part[0].isupper() for part in cardholder_name.split() if part):
                raise ValueError('Неверное имя держателя карты')
            # Проверка CVV
            if not cvv.isdigit() or len(cvv) not in (3, 4):
                raise ValueError('Неверный CVV')
            # Фиктивная успешная транзакция
            return {'status': 'success', 'transaction_id': f'TXN-{int(total_amount * 100)}-{card_number[-4:]}'}
        elif payment_method == 'sbp':
            # Фиктивный платеж через СБП
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
                    # Проверка валидности данных карты, если выбрана карта
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
        cart_html = render_to_string('products/basket.html', {'baskets': baskets, 'total_sum': total_sum})
        return JsonResponse({
            'total_items': baskets.count(),
            'total_sum': float(total_sum),
            'cart_html': cart_html
        })
    except Exception as e:
        logger.error(f"Ошибка при синхронизации корзины: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Ошибка синхронизации корзины'}, status=500)