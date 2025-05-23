from django.urls import path
from products.views import products, products_list

app_name = "products"

urlpatterns = [
    path('', products, name="index"),
    path('products_list/', products_list, name="products_list"),
]
