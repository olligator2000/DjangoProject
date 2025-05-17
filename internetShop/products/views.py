from django.shortcuts import render
from products.models import Product, ProductCategory


def index(request):
    categories = ProductCategory.objects.prefetch_related('products').all()
    first_category = categories.first()

    context = {
        "title": "store",
        "categories": categories,
        "products": first_category.products.all() if first_category else [],
        "show_products": False
    }
    return render(request, "products/index.html", context)


def products(request):
    context = {
        "title": "store - products",
    }
    return render(request, "products/products.html", context)


def products_list(request):
    return render(request, "products/products_list.html")
