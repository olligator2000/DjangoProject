from django.urls import path
from . import views
from products.views import (
    IndexView, products, products_list, product_detail,
    add_to_cart_ajax, update_basket_ajax,
    clear_basket_ajax, category_products, get_products_by_category, get_random_products, search_products, zakaz_end,
    order_confirmation, rate_product, filter_products, submit_review
)

app_name = "products"

urlpatterns = [
    path('', products, name="index"),
    path('products-list/', products_list, name="products_list"),
    path('category/<int:category_id>/', category_products, name="category_products"),
    path('<int:product_id>/', product_detail, name="product_detail"),
    path('add_to_cart_ajax/<int:product_id>/', add_to_cart_ajax, name='add_to_cart_ajax'),
    path('update_basket_ajax/<int:basket_id>/<str:action>/', update_basket_ajax, name='update_basket_ajax'),
    path('clear_basket_ajax/', clear_basket_ajax, name='clear_basket_ajax'),
    path('api/products/', get_products_by_category, name='api_products'),
    path('get_random_products/', views.get_random_products, name='get_random_products'),
    path('search/', search_products, name='search_products'),
    path('zakaz_end/', zakaz_end, name='zakaz_end'),
    path('get_cart_state/', views.get_cart_state, name='get_cart_state'),
    path('order_confirmation/', order_confirmation, name='order_confirmation'),
    path('rate_product/', rate_product, name='rate_product'),
    path('<int:product_id>/rate/', rate_product, name='rate_product_detail'),  # Новый путь
    path('filter_products/', filter_products, name='filter_products'),
    path('<int:product_id>/review/', views.submit_review, name='submit_review'),
]